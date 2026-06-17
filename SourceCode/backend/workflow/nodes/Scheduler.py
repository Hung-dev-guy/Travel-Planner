"""
workflow/nodes/Scheduler.py

Scheduler Node — Logic-First Day-by-Day Itinerary Planning.

Takes activities, accommodations, and transportations from previous nodes
and creates a comprehensive day-by-day schedule respecting:
  - Total trip duration
  - Daily active hours
  - Budget constraints
  - Travel preferences & pace
  - Suitability for companion types
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from workflow.graph.stage import State
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()


# ==========================================
# DATA MODELS
# ==========================================

class ScheduleItem(BaseModel):
    """A single scheduled event (activity, meal, transport, accommodation)."""
    time_start: str
    time_end: str
    type: str  # transportation, activity, accommodation, meal, rest
    name: str
    location: str
    description: Optional[str] = None
    duration_minutes: int = 0
    cost: int = 0
    notes: Optional[str] = None
    img_url: Optional[str] = None


class DaySummary(BaseModel):
    """Summary statistics for a single day."""
    total_cost: int = 0
    activities_count: int = 0
    meals_count: int = 0
    travel_time_hours: float = 0
    active_hours: float = 0
    rest_hours: float = 0
    highlights: List[str] = []
    energy_level: str = "moderate"  # low, moderate, high


class DaySchedule(BaseModel):
    """Complete schedule for one day."""
    day: int
    date: str
    title: str
    items: List[Dict[str, Any]] = []
    day_summary: Dict[str, Any] = {}


class SchedulingOutput(BaseModel):
    """Final output: list of daily schedules."""
    scheduling: List[Dict[str, Any]] = Field(
        description="Danh sách lịch trình theo ngày. Mỗi ngày chứa thông tin: day, date, title, items, day_summary."
    )


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def time_to_minutes(time_str: str) -> int:
    """Convert HH:MM to minutes since midnight."""
    try:
        h, m = map(int, time_str.split(":"))
        return h * 60 + m
    except:
        return 0


def minutes_to_time(minutes: int) -> str:
    """Convert minutes since midnight to HH:MM."""
    h = (minutes // 60) % 24
    m = minutes % 60
    return f"{h:02d}:{m:02d}"


def calculate_duration(start: str, end: str) -> int:
    """Calculate duration in minutes between two times."""
    start_min = time_to_minutes(start)
    end_min = time_to_minutes(end)
    
    if end_min < start_min:  # Spans midnight
        end_min += 24 * 60
    
    return end_min - start_min


COMPANION_MAP = {
    "gia đình": "Family",
    "trẻ nhỏ": "Kids",
    "trẻ em": "Kids",
    "người già": "Elderly",
    "lớn tuổi": "Elderly",
    "cặp đôi": "Couples",
    "bạn bè": "Friends",
    "một mình": "Solo",
    "nhóm": "Group"
}

def matches_suitability(item: Dict, companion_types: List[str]) -> bool:
    """Check if item is suitable for the given companion types."""
    if not companion_types:
        return True
    suitability = item.get("suitability_for", item.get("suitabilityFor", []))
    if not suitability:
        return True
    
    # Translate Vietnamese tags to English
    translated_ct = []
    for ct in companion_types:
        ct_lower = ct.lower()
        for vi, en in COMPANION_MAP.items():
            if vi in ct_lower:
                translated_ct.append(en)
        translated_ct.append(ct)
        
    return any(ct in suitability for ct in translated_ct)


def select_best_activity(
    available_activities: List[Dict],
    time_available_minutes: int,
    budget_available: int,
    companion_types: List[str],
    already_selected_ids: set,
    group_size: int = 1
) -> Optional[Dict]:
    """Select best activity that fits time, budget, and suitability."""
    candidates = []
    
    for activity in available_activities:
        activity_id = activity.get("_id") or activity.get("name")
        if activity_id in already_selected_ids:
            continue
            
        if activity.get("name") == "string" or activity.get("locationId") == "string":
            continue
        
        duration = activity.get("estimatedDuration", activity.get("estimated_duration_minutes", 60))
        base_cost = activity.get("estimated_cost", activity.get("estimatedPrice", activity.get("cost", 0)))
        cost = base_cost * group_size
        
        # Check constraints
        if duration > time_available_minutes:
            continue
        if cost > budget_available:
            continue
        if not matches_suitability(activity, companion_types):
            continue
        
        # Score by suitability and cost efficiency
        item_suitability = activity.get("suitability_for", activity.get("suitabilityFor", []))
        suitability_score = sum(1 for ct in companion_types if ct in item_suitability)
        cost_efficiency = (1 - cost / max(budget_available, 1)) if cost > 0 else 0.5
        
        score = (suitability_score * 2) + cost_efficiency
        candidates.append((score, activity))
    
    if candidates:
        # Sort by score (first element of tuple) in descending order
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]
    
    return None


# ==========================================
# MAIN SCHEDULING LOGIC
# ==========================================

def create_daily_schedule(
    day_num: int,
    date_str: str,
    activities: List[Dict],
    accommodations: List[Dict],
    transportations: List[Dict],
    constraints: Dict,
    travel_preferences: Dict,
    is_arrival_day: bool = False,
    is_departure_day: bool = False,
    total_days: int = 1,
    start_location: str = "Hà Nội",
) -> DaySchedule:
    """Create schedule for a single day."""
    
    day_schedule = {
        "day": day_num,
        "date": date_str,
        "title": "",
        "items": [],
        "day_summary": {
            "total_cost": 0,
            "activities_count": 0,
            "meals_count": 0,
            "travel_time_hours": 0,
            "active_hours": 0,
            "rest_hours": 0,
            "highlights": [],
            "energy_level": "moderate",
        }
    }
    
    items = []
    current_time_min = time_to_minutes("06:00")  # Start at 6 AM
    end_time_min = time_to_minutes("22:00")  # End at 10 PM
    
    try:
        travel_budget_val = int(constraints.get("travel_budget", 1_000_000))
    except (ValueError, TypeError):
        travel_budget_val = 1_000_000
        
    try:
        group_size_val = int(constraints.get("group_size", 1))
    except (ValueError, TypeError):
        group_size_val = 1
        
    daily_budget = travel_budget_val / max(total_days, 1)
    spent_today = 0
    companion_types = travel_preferences.get("companion_type", [])
    already_selected = set()
    
    # ── Arrival Day ──────────────────────────────────────────────────────────
    if is_arrival_day and transportations:
        transport = transportations[0]
        departure_time = transport.get("schedule", [{}])[0].get("departure", "06:00") if transport.get("schedule") else "06:00"
        arrival_time = transport.get("schedule", [{}])[0].get("arrival", "09:00") if transport.get("schedule") else "09:00"
        
        item = {
            "time_start": departure_time,
            "time_end": arrival_time,
            "type": "transportation",
            "name": transport.get("name", "Transport to destination"),
            "location": transport.get("to_ward", "Destination"),
            "locationId": transport.get("_id"),
            "description": f"Travel from {transport.get('from_ward')} to {transport.get('to_ward')}",
            "duration_minutes": calculate_duration(departure_time, arrival_time),
            "cost": transport.get("price_per_person", 0) * group_size_val,
            "notes": "Bring snacks and stay hydrated",
            "img_url": transport.get("img_url", None)
        }
        items.append(item)
        spent_today += item["cost"]
        current_time_min = time_to_minutes(arrival_time)
        day_schedule["title"] = "🛫 Arrival Day"
    
    # ── Departure Day ────────────────────────────────────────────────────────
    elif is_departure_day and transportations:
        # Find return transport
        return_transport = next((t for t in transportations if t.get("to_ward") == start_location), transportations[-1])
        departure_time = return_transport.get("schedule", [{}])[0].get("departure", "17:00") if return_transport.get("schedule") else "17:00"
        arrival_time = return_transport.get("schedule", [{}])[0].get("arrival", "20:00") if return_transport.get("schedule") else "20:00"
        
        # Add morning activity
        budget_left = daily_budget - spent_today
        activity = select_best_activity(activities, time_to_minutes(departure_time) - current_time_min, int(budget_left * 0.3), companion_types, already_selected)
        
        if activity:
            item = {
                "time_start": minutes_to_time(current_time_min),
                "time_end": "12:00",
                "type": "activity",
                "name": activity.get("name", "Activity"),
                "location": activity.get("ward_name", "Location"),
                "locationId": activity.get("_id"),
                "description": activity.get("description", ""),
                "duration_minutes": calculate_duration(minutes_to_time(current_time_min), "12:00"),
                "cost": activity.get("estimated_cost", activity.get("estimatedPrice", activity.get("cost", 0))) * group_size_val,
                "notes": "Last activity before departure",
                "img_url": activity.get("img_url", None),
                "suitability": activity.get("suitability_for", activity.get("suitabilityFor", []))
            }
            items.append(item)
            spent_today += item["cost"]
            already_selected.add(activity.get("_id") or activity.get("name"))
        
        # Add lunch
        item = {
            "time_start": "12:00",
            "time_end": "13:00",
            "type": "meal",
            "name": "Lunch",
            "location": "Local Restaurant",
            "description": "Final meal before departure",
            "duration_minutes": 60,
            "cost": 150_000 * group_size_val,
            "img_url": None
        }
        items.append(item)
        spent_today += item["cost"]
        
        # Add departure transport
        item = {
            "time_start": departure_time,
            "time_end": arrival_time,
            "type": "transportation",
            "name": return_transport.get("name", "Transport back"),
            "location": return_transport.get("to_ward", start_location),
            "locationId": return_transport.get("_id"),
            "description": f"Return trip to {return_transport.get('to_ward')}",
            "duration_minutes": calculate_duration(departure_time, arrival_time),
            "cost": return_transport.get("price_per_person", 0) * group_size_val,
            "notes": "Check-out before departure",
            "img_url": return_transport.get("img_url", None)
        }
        items.append(item)
        spent_today += item["cost"]
        day_schedule["title"] = "🛬 Departure Day"
    
    # ── Normal Day ───────────────────────────────────────────────────────────
    else:
        day_schedule["title"] = f"📍 Day {day_num} - Exploration"
        budget_left = daily_budget - spent_today
        
        # Parse travel pace for dynamic scheduling
        paces = [p.lower() for p in travel_preferences.get("travel_pace", [])]
        is_relaxed = any("thong thả" in p or "chậm" in p or "chill" in p for p in paces)
        is_fast = any("nhanh" in p or "năng động" in p for p in paces)
        
        rest_duration = 60 if is_relaxed else 15 if is_fast else 30
        
        # Breakfast
        breakfast_end = "08:00" if is_relaxed else "07:30"
        item = {
            "time_start": minutes_to_time(current_time_min),
            "time_end": breakfast_end,
            "type": "meal",
            "name": "Breakfast",
            "location": "Hotel/Accommodation",
            "cost": 100_000 * group_size_val,
            "img_url": None
        }
        items.append(item)
        spent_today += item["cost"]
        current_time_min = time_to_minutes(breakfast_end)
        budget_left -= item["cost"]
        
        had_lunch = False
        had_dinner = False
        
        # Loop to fill the day dynamically until dinner is scheduled
        while current_time_min < time_to_minutes("21:00") and not had_dinner:
            # Check for Lunch (schedule if it's past 11:30 and haven't eaten)
            if not had_lunch and current_time_min >= time_to_minutes("11:30"):
                lunch_end = current_time_min + (90 if is_relaxed else 60)
                item = {
                    "time_start": minutes_to_time(current_time_min),
                    "time_end": minutes_to_time(lunch_end),
                    "type": "meal",
                    "name": "Lunch - Local Cuisine",
                    "location": "Local Restaurant",
                    "cost": 120_000 * group_size_val,
                    "img_url": None
                }
                items.append(item)
                spent_today += item["cost"]
                budget_left -= item["cost"]
                current_time_min = lunch_end
                had_lunch = True
                
                # Rest after lunch
                current_time_min += rest_duration
                continue
                
            # Check for Dinner (schedule if it's past 18:00 and haven't eaten)
            if not had_dinner and current_time_min >= time_to_minutes("18:00"):
                dinner_end = current_time_min + (120 if is_relaxed else 90)
                item = {
                    "time_start": minutes_to_time(current_time_min),
                    "time_end": minutes_to_time(dinner_end),
                    "type": "meal",
                    "name": "Dinner - Local Specialties",
                    "location": "Local Restaurant",
                    "cost": 150_000 * group_size_val,
                    "img_url": None
                }
                items.append(item)
                spent_today += item["cost"]
                budget_left -= item["cost"]
                current_time_min = dinner_end
                had_dinner = True
                break
            
            # Try to schedule an activity
            if not had_lunch:
                time_until_next_event = time_to_minutes("12:00") - current_time_min
            else:
                time_until_next_event = time_to_minutes("18:30") - current_time_min
                
            # If time is too short for any activity, skip to next meal time
            if time_until_next_event < 45:
                current_time_min += time_until_next_event
                continue
                
            activity = select_best_activity(activities, time_until_next_event, int(budget_left * 0.5), companion_types, already_selected, group_size_val)
            
            if activity:
                dur = activity.get("estimatedDuration", activity.get("estimated_duration_minutes", 120))
                # Adjust duration based on pace
                if is_relaxed: dur = int(dur * 1.2)
                elif is_fast: dur = int(dur * 0.8)
                
                # Cap duration to fit before the next event
                dur = min(dur, time_until_next_event)
                
                item = {
                    "time_start": minutes_to_time(current_time_min),
                    "time_end": minutes_to_time(current_time_min + dur),
                    "type": "activity",
                    "name": activity.get("name", "Activity"),
                    "location": activity.get("ward_name", "Location"),
                    "locationId": activity.get("_id"),
                    "description": activity.get("description", ""),
                    "duration_minutes": dur,
                    "cost": activity.get("estimated_cost", activity.get("estimatedPrice", activity.get("cost", 0))) * group_size_val,
                    "img_url": activity.get("img_url", None),
                    "suitability": activity.get("suitability_for", activity.get("suitabilityFor", []))
                }
                items.append(item)
                spent_today += item["cost"]
                already_selected.add(activity.get("_id") or activity.get("name"))
                budget_left -= item["cost"]
                current_time_min += dur
                day_schedule["day_summary"]["highlights"].append(activity.get("name", ""))
                
                # Add rest after activity
                current_time_min += rest_duration
            else:
                # No affordable/suitable activity fits, skip to next event time
                current_time_min += time_until_next_event
    
    # ── Accommodation ────────────────────────────────────────────────────────
    if accommodations and day_num <= len(accommodations):
        accommodation = accommodations[day_num - 1]
        item = {
            "time_start": "20:00",
            "time_end": "08:00",  # Next day
            "type": "accommodation",
            "name": accommodation.get("name", "Hotel"),
            "location": accommodation.get("ward_name", "Location"),
            "locationId": accommodation.get("_id"),
            "cost": accommodation.get("price_per_night", accommodation.get("estimatedPrice", 0)) * group_size_val,
            "notes": f"Check-in at 15:00, Check-out at 10:00",
            "img_url": accommodation.get("img_url", None)
        }
        items.append(item)
        spent_today += item["cost"]
    
    # ── Finalize day ────────────────────────────────────────────────────────
    day_schedule["items"] = items
    
    # Calculate summary
    total_cost = sum(item.get("cost", 0) for item in items)
    activities_count = sum(1 for item in items if item.get("type") == "activity")
    meals_count = sum(1 for item in items if item.get("type") == "meal")
    travel_time = sum(item.get("duration_minutes", 0) for item in items if item.get("type") == "transportation") / 60
    
    day_schedule["day_summary"] = {
        "total_cost": total_cost,
        "activities_count": activities_count,
        "meals_count": meals_count,
        "travel_time_hours": round(travel_time, 1),
        "active_hours": round((time_to_minutes("22:00") - current_time_min) / 60, 1),
        "rest_hours": round((current_time_min - time_to_minutes("06:00")) / 60, 1),
        "highlights": day_schedule["day_summary"].get("highlights", []),
        "energy_level": "high" if activities_count >= 2 else "moderate" if activities_count == 1 else "low",
    }
    
    return day_schedule


# ==========================================
# MAIN SCHEDULER NODE
# ==========================================

# ==========================================
# VALIDATION FEEDBACK HANDLING
# ==========================================

def apply_validation_feedback(
    state_activities: List[Dict],
    state_constraints: Dict,
    feedback: List[Dict],
) -> tuple:
    """
    Adjust activities and constraints based on validation recommendations.
    
    Handles:
    - budget: Remove most expensive activities to bring cost down
    - time: Reduce daily active hours or cap activities per day
    - balance: Limit activities per day to avoid over-packing
    - activity_suitability: Deprioritize poorly-matching activities
    
    Returns: (adjusted_activities, adjusted_constraints)
    """
    import logging
    log = logging.getLogger(__name__)
    
    activities = list(state_activities)  # shallow copy to avoid mutating original
    constraints = dict(state_constraints)
    
    # Sort recommendations: high priority first
    priority_order = {"high": 0, "medium": 1, "low": 2}
    sorted_feedback = sorted(feedback, key=lambda r: priority_order.get(r.get("priority", "low"), 3))
    
    for rec in sorted_feedback:
        category = rec.get("category", "")
        
        if category == "budget":
            # Remove the most expensive activity to reduce overall cost
            if activities:
                activities_sorted = sorted(
                    activities,
                    key=lambda a: a.get("estimated_cost", a.get("estimatedPrice", a.get("cost", 0))),
                    reverse=True
                )
                removed = activities_sorted[0]
                activities = [a for a in activities if a is not removed]
                log.info(f"[Feedback] Removed expensive activity '{removed.get('name')}' to reduce budget")
        
        elif category == "time":
            # Tighten daily_active_hours by 1 hour if over the limit
            current_hours = int(constraints.get("daily_active_hours", 10))
            if current_hours > 6:
                constraints = dict(constraints)
                constraints["daily_active_hours"] = current_hours - 1
                log.info(f"[Feedback] Reduced daily_active_hours from {current_hours} to {constraints['daily_active_hours']}")
        
        elif category == "balance":
            # Cap activities at 2 per day — drop extras from the end
            if len(activities) > 2:
                activities = activities[:max(2, len(activities) - 1)]
                log.info(f"[Feedback] Trimmed activity pool to {len(activities)} for better balance")
        
        elif category == "activity_suitability":
            # Move poorly-matching activities to the back so they are selected last
            travel_style = constraints.get("travel_style", [])
            if isinstance(travel_style, str):
                travel_style = [travel_style]
            
            def suitability_key(a):
                cat = a.get("category", "").lower()
                suits = str(a.get("suitabilityFor", a.get("suitability", []))).lower()
                match = any(s.lower() in cat or s.lower() in suits for s in travel_style)
                return 0 if match else 1  # matched activities sort first
            
            activities = sorted(activities, key=suitability_key)
            log.info("[Feedback] Reordered activities by suitability match")
    
    return activities, constraints


def scheduler_node(state: dict) -> dict:
    """
    Scheduler node — Create day-by-day itinerary.
    
    Input: activities, accommodations, transportations from previous nodes
    Output: scheduling (list of daily schedules)
    
    Note: Handles both Planner node output (accommodation, activities, eateries)
          and direct state fields (accommodations, activities, transportations).
          Also handles validation_feedback when called during the feedback loop.
    """
    
    trip_metadata = state.get("trip_metadata", {})
    travel_preferences = state.get("travel_preferences", {})
    constraints = state.get("constraints", {})
    
    # Support both naming conventions: 
    # - State field names (activities, accommodations, transportations)
    # - Planner output names (activity, accommodation, eateries)
    activities = state.get("activities", [])
    if not activities:
        activities = state.get("activity", [])
    
    accommodations = state.get("accommodations", [])
    if not accommodations:
        accommodations = state.get("accommodation", [])
    
    transportations = state.get("transportations", [])
    
    def _to_dict(obj):
        if isinstance(obj, dict): return obj
        try:
            return obj.model_dump()
        except AttributeError:
            pass
        try:
            return obj.dict()
        except AttributeError:
            pass
        try:
            return dict(obj)
        except (TypeError, ValueError):
            pass
        try:
            return vars(obj)
        except TypeError:
            pass
        return obj
        
    activities = [_to_dict(a) for a in activities]
    accommodations = [_to_dict(a) for a in accommodations]
    transportations = [_to_dict(t) for t in transportations]
    
    # ── Apply validation feedback if present (feedback loop iteration) ────────
    feedback = state.get("validation_feedback", [])
    if feedback:
        import logging
        logging.getLogger(__name__).info(
            f"Applying {len(feedback)} validation recommendation(s) before rescheduling"
        )
        activities, constraints = apply_validation_feedback(activities, constraints, feedback)
        # Clear feedback so it isn't re-applied on subsequent scheduler calls
        state["validation_feedback"] = []
    
    # Extract trip dates
    start_date_str = trip_metadata.get("start_date", "2026-06-01")
    total_days = int(trip_metadata.get("total_days", 3))
    start_location_raw = trip_metadata.get("start_location", "Hà Nội")
    start_location = start_location_raw.split(",")[0].strip() if start_location_raw else "Hà Nội"
    
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    except:
        start_date = datetime.now()
    
    # Create daily schedules
    scheduling = []
    
    for day_num in range(1, total_days + 1):
        current_date = start_date + timedelta(days=day_num - 1)
        date_str = current_date.strftime("%Y-%m-%d")
        
        is_arrival = day_num == 1
        is_departure = day_num == total_days
        
        day_schedule = create_daily_schedule(
            day_num=day_num,
            date_str=date_str,
            activities=activities,
            accommodations=accommodations,
            transportations=transportations,
            constraints=constraints,
            travel_preferences=travel_preferences,
            is_arrival_day=is_arrival,
            is_departure_day=is_departure,
            total_days=total_days,
            start_location=start_location,
        )
        
        scheduling.append(day_schedule)
    
    # Update state with scheduling
    state["scheduling"] = scheduling
    
    return state


# Alias used by the graph builder
scheduling_node = scheduler_node
