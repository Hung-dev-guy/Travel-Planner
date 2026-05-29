"""
run_pipeline.py
Full pipeline integration test: Mobility → Scheduler → Validation → Generate_answer

Covers the last 4 nodes in the pipeline (Extractor and Planner are LLM-only,
tested separately via test_extractor.py and test_planner.py).

Usage:
    cd backend/
    .venv/bin/python workflow/test/run_pipeline.py
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from workflow.nodes.Mobility_agent import mobility_node
from workflow.nodes.Scheduler import scheduler_node
from workflow.nodes.Validation_agent import validation_node
from workflow.nodes.Generate_answer import generate_answer_node
from workflow.db import reset_mongo_connection, get_mongo_db

DIVIDER = "=" * 70
SECTION  = "-" * 70


def section(title: str):
    print(f"\n{SECTION}")
    print(f"  {title}")
    print(SECTION)


def header(title: str):
    print(f"\n{DIVIDER}")
    print(f"  {title}")
    print(DIVIDER)


def json_preview(obj, max_chars: int = 2000) -> str:
    """Return truncated JSON string for display."""
    s = json.dumps(obj, indent=2, ensure_ascii=False, default=str)
    if len(s) > max_chars:
        return s[:max_chars] + f"\n... (truncated, {len(s)} chars total)"
    return s


# ─────────────────────────────────────────────────────────────────────────────
# MOCK / FALLBACK DATA
# ─────────────────────────────────────────────────────────────────────────────

MOCK_ACTIVITIES = [
    {
        "_id": "act_001",
        "name": "Hạ Long Bay Cruise",
        "description": "UNESCO World Heritage limestone karsts cruise",
        "ward_name": "Hạ Long",
        "estimatedPrice": 150_000,
        "estimatedDuration": 180,
        "suitabilityFor": ["Couples", "Family"],
        "category": "nature",
        "atmosphere": "scenic",
    },
    {
        "_id": "act_002",
        "name": "Sung Sot Cave Exploration",
        "description": "Famous limestone cave with stunning formations",
        "ward_name": "Bạch Đằng",
        "estimatedPrice": 80_000,
        "estimatedDuration": 120,
        "suitabilityFor": ["Couples", "Group", "Solo"],
        "category": "cultural",
        "atmosphere": "adventurous",
    },
    {
        "_id": "act_003",
        "name": "Titop Island Beach",
        "description": "Beautiful beach with crystal clear water",
        "ward_name": "Hạ Long",
        "estimatedPrice": 50_000,
        "estimatedDuration": 240,
        "suitabilityFor": ["Couples", "Family"],
        "category": "nature",
        "atmosphere": "relaxing",
    },
    {
        "_id": "act_004",
        "name": "Mong Cai Border Market",
        "description": "Traditional border trading town experience",
        "ward_name": "Mong Cai",
        "estimatedPrice": 30_000,
        "estimatedDuration": 150,
        "suitabilityFor": ["Couples", "Group", "Solo"],
        "category": "cultural",
        "atmosphere": "cultural",
    },
]

MOCK_ACCOMMODATIONS = [
    {
        "_id": "acc_001",
        "name": "Halong Bay Hotel",
        "ward_name": "Hạ Long",
        "estimatedPrice": 200_000,
        "accommodation_style": "comfortable",
        "quality_level": "comfortable",
    },
    {
        "_id": "acc_002",
        "name": "Halong Bay Hotel",
        "ward_name": "Hạ Long",
        "estimatedPrice": 200_000,
        "accommodation_style": "comfortable",
        "quality_level": "comfortable",
    },
    {
        "_id": "acc_003",
        "name": "Halong Bay Hotel",
        "ward_name": "Hạ Long",
        "estimatedPrice": 200_000,
        "accommodation_style": "comfortable",
        "quality_level": "comfortable",
    },
]

MOCK_TRANSPORTATIONS = [
    {
        "name": "Coach (Hà Nội → Hạ Long)",
        "type": "coach",
        "from_ward": "Hà Nội",
        "to_ward": "Hạ Long",
        "distance_km": 160.0,
        "price_per_person": 125_000,
        "schedule": [{"departure": "06:00", "arrival": "09:00"}],
    },
    {
        "name": "Coach (Hạ Long → Hà Nội)",
        "type": "coach",
        "from_ward": "Hạ Long",
        "to_ward": "Hà Nội",
        "distance_km": 160.0,
        "price_per_person": 125_000,
        "schedule": [{"departure": "17:00", "arrival": "20:00"}],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def parse_daily_active_hours(raw) -> int:
    """
    Convert daily_active_hours constraint to an integer.
    Accepts: int, float, '8', '8-10' (takes the lower bound), '10h', etc.
    """
    if isinstance(raw, (int, float)):
        return int(raw)
    if isinstance(raw, str):
        raw = raw.strip().lower().replace("h", "").replace(" ", "")
        if "-" in raw:
            return int(raw.split("-")[0])
        try:
            return int(float(raw))
        except ValueError:
            pass
    return 10  # safe default


def load_activities_from_mongo() -> list:
    """Fetch activities from MongoDB; returns [] on any error."""
    try:
        db = get_mongo_db("TravelPlanner")
        docs = list(db["Locations"].find(
            {"category": {"$in": ["nature", "adventure", "cultural", "viewpoint"]}},
            {"_id": 1, "name": 1, "description": 1, "ward_name": 1,
             "estimatedPrice": 1, "estimatedDuration": 1,
             "suitabilityFor": 1, "category": 1},
        ))
        for d in docs:
            d["_id"] = str(d["_id"])
        return docs
    except Exception as e:
        print(f"  ⚠️  MongoDB fetch failed: {e}")
        return []


# ─────────────────────────────────────────────────────────────────────────────
# PIPELINE RUNNER
# ─────────────────────────────────────────────────────────────────────────────

def run_full_pipeline():
    header("FULL PIPELINE INTEGRATION TEST")
    print("  Nodes: Mobility → Scheduler → Validation → Generate_answer\n")

    reset_mongo_connection()

    # ──────────────────────────────────────────────────────────────────────────
    # STEP 0: Build initial state
    # ──────────────────────────────────────────────────────────────────────────
    section("STEP 0: Build Initial State")

    state = {
        # Raw input
        "user_des_input": (
            "Tôi muốn đi du lịch Quảng Ninh vào tháng 6 này, 2 người, "
            "thích đi thong thả, khám phá thiên nhiên và văn hóa, ngân sách "
            "khoảng 300k mỗi người."
        ),
        "group_size": 2,
        "start_date": "2026-06-01",
        "end_date": "2026-06-03",
        "start_location": "Hà Nội",
        "destination": ["Quảng Ninh"],
        "personal_travel_style_des": "Lãng mạn, thong thả, du lịch nhẹ nhàng",

        # Structured metadata (normally produced by Extractor)
        "trip_metadata": {
            "usr_des": "Tôi muốn đi du lịch Quảng Ninh 3 ngày",
            "start_date": "2026-06-01",
            "end_date": "2026-06-03",
            "total_days": "3",
            "age_range": "25-40",
            "start_location": "Hà Nội",
            "destination": "Quảng Ninh",
        },

        # Constraints
        "constraints": {
            "travel_budget": 2_000_000,   # 2M VNĐ total (1M/person × 2 people)
            "group_size": 2,
            "daily_active_hours": "8-10",
            "language": "Vietnamese",
            "max_radius_distance": 50,
            "places_of_limitation": [],
            "health_limitations": [],
            "mobility_limitations": [],
        },

        # Travel preferences (normally produced by Extractor)
        "travel_preferences": {
            "travel_style": ["nature", "cultural"],
            "travel_pace": ["thong thả"],
            "food_style": ["local", "seafood"],
            "accommodation_style": ["comfortable"],
            "mobility_style": ["flexible"],
            "atmosphere": ["lãng mạn"],
            "companion_type": ["Couples"],
        },

        # Pipeline outputs (empty initially)
        "activities": [],
        "accommodations": [],
        "transportations": [],
        "scheduling": [],
        "validation": None,
        "validation_feedback": [],
        "validation_iteration": 1,
        "final_answer": None,
    }

    print(f"  Destination : {state['trip_metadata']['destination']}")
    print(f"  Dates       : {state['trip_metadata']['start_date']} → {state['trip_metadata']['end_date']}")
    print(f"  Group size  : {state['constraints']['group_size']} people")
    print(f"  Budget      : {state['constraints']['travel_budget']:,} VNĐ total")

    # ──────────────────────────────────────────────────────────────────────────
    # STEP 1: Mobility_agent
    # ──────────────────────────────────────────────────────────────────────────
    section("STEP 1: Mobility_agent (Neo4j routes + MongoDB providers + AI ranking)")

    try:
        state = mobility_node(state)
        transportations = state.get("transportations", [])
        print(f"\n  ✅ Mobility_agent OK → {len(transportations)} transport options found")

        if transportations:
            print("\n  🚗 Top transport options:")
            for idx, t in enumerate(transportations[:4], 1):
                print(f"    [{idx}] {t.get('name')} | {t.get('type')} | "
                      f"{t.get('distance_km', 0):.0f} km | "
                      f"{t.get('price_per_person', 0):,} VNĐ/person")
        else:
            print("  ⚠️  No transport options — using mock data")
            state["transportations"] = MOCK_TRANSPORTATIONS

    except Exception as e:
        print(f"\n  ❌ Mobility_agent FAILED: {e}")
        import traceback; traceback.print_exc()
        print("  ⚠️  Falling back to mock transport data")
        state["transportations"] = MOCK_TRANSPORTATIONS

    # ──────────────────────────────────────────────────────────────────────────
    # Load activities (from MongoDB or mock)
    # ──────────────────────────────────────────────────────────────────────────
    section("STEP 1b: Load Activities & Accommodations")

    activities = load_activities_from_mongo()
    if activities:
        print(f"  ✅ Loaded {len(activities)} activities from MongoDB (TravelPlanner.Locations)")
        state["activities"] = activities
    else:
        print(f"  ⚠️  Using {len(MOCK_ACTIVITIES)} mock activities")
        state["activities"] = MOCK_ACTIVITIES

    if not state.get("accommodations"):
        print(f"  ⚠️  No accommodations from Planner — using {len(MOCK_ACCOMMODATIONS)} mock entries")
        state["accommodations"] = MOCK_ACCOMMODATIONS

    # ──────────────────────────────────────────────────────────────────────────
    # STEP 2: Scheduler
    # ──────────────────────────────────────────────────────────────────────────
    section("STEP 2: Scheduler (day-by-day itinerary builder)")

    try:
        state = scheduler_node(state)
        scheduling = state.get("scheduling", [])
        print(f"\n  ✅ Scheduler OK → {len(scheduling)} days scheduled")

        total_cost = 0
        for day in scheduling:
            summary = day.get("day_summary", {})
            day_cost = summary.get("total_cost", 0)
            total_cost += day_cost
            acts = summary.get("activities_count", 0)
            meals = summary.get("meals_count", 0)
            print(f"\n  📅 Day {day['day']}: {day['title']}")
            print(f"     Cost: {day_cost:,} VNĐ | Activities: {acts} | Meals: {meals}")
            for item in day.get("items", []):
                icon = {"activity": "🎯", "meal": "🍽️", "accommodation": "🏨",
                        "transportation": "🚌", "transport": "🚌"}.get(item.get("type"), "•")
                print(f"     {icon} {item.get('name', '?')}  "
                      f"({item.get('time_start', '??:??')}–{item.get('time_end', '??:??')})  "
                      f"{item.get('cost', 0):,} VNĐ")

        print(f"\n  💰 Total trip cost: {total_cost:,} VNĐ")
        print(f"     Per person: {total_cost // max(state['constraints']['group_size'], 1):,} VNĐ")

    except Exception as e:
        print(f"\n  ❌ Scheduler FAILED: {e}")
        import traceback; traceback.print_exc()
        return False

    # ──────────────────────────────────────────────────────────────────────────
    # STEP 3: Validation (normalize daily_active_hours first)
    # ──────────────────────────────────────────────────────────────────────────
    section("STEP 3: Validation (7-criteria quality gate)")

    # Normalize daily_active_hours to int so Validation_agent can compare
    raw_hours = state["constraints"].get("daily_active_hours", 10)
    state["constraints"]["daily_active_hours"] = parse_daily_active_hours(raw_hours)

    # Also expose accommodation_style as a scalar for validation
    accom_style = state["travel_preferences"].get("accommodation_style", ["comfortable"])
    if isinstance(accom_style, list):
        state["travel_preferences"]["accommodation_style"] = accom_style[0] if accom_style else "comfortable"

    try:
        state = validation_node(state)
        val = state.get("validation", {})

        score  = val.get("overall_score", 0)
        status = val.get("status", "UNKNOWN")
        status_icon = "✅" if status == "APPROVED" else "⚠️" if status == "NEEDS_IMPROVEMENT" else "❌"

        print(f"\n  {status_icon} Validation complete")
        print(f"     Overall score : {score:.1f} / 100")
        print(f"     Status        : {status}")

        print("\n  📊 Category scores:")
        for cat, cat_score in val.get("category_scores", {}).items():
            bar = "✅" if cat_score >= 7 else "⚠️" if cat_score >= 5 else "❌"
            print(f"     {bar}  {cat.replace('_', ' ').title():<28}: {cat_score:.1f} pts")

        issues = val.get("issues", [])
        critical = [i for i in issues if i.get("severity") == "critical"]
        warnings  = [i for i in issues if i.get("severity") == "warning"]
        print(f"\n  📋 Issues: {len(issues)} total "
              f"({len(critical)} critical, {len(warnings)} warnings)")
        for issue in issues:
            sev = issue.get("severity", "info")
            icon = "🔴" if sev == "critical" else "🟡" if sev == "warning" else "ℹ️"
            day_tag = f" (Day {issue['day']})" if issue.get("day") else ""
            print(f"     {icon}  {issue['message']}{day_tag}")

        recs = val.get("recommendations", [])
        if recs:
            print(f"\n  💡 Recommendations ({len(recs)}):")
            for r in recs:
                prio_icon = "🔥" if r.get("priority") == "high" else "⚠️" if r.get("priority") == "medium" else "💬"
                print(f"     {prio_icon}  [{r.get('priority','?').upper()}] {r.get('suggestion')}")

    except Exception as e:
        print(f"\n  ❌ Validation FAILED: {e}")
        import traceback; traceback.print_exc()
        return False

    # ──────────────────────────────────────────────────────────────────────────
    # STEP 4: Generate_answer
    # ──────────────────────────────────────────────────────────────────────────
    section("STEP 4: Generate_answer (final structured output)")

    try:
        state = generate_answer_node(state)
        answer = state.get("final_answer", {})

        print(f"\n  ✅ Generate_answer OK")
        print(f"     Status message : {answer.get('status_message', 'N/A')}")
        print(f"     Generated at   : {answer.get('generated_at', 'N/A')}")

        overview = answer.get("trip_overview", {})
        print(f"\n  🗺️  Trip Overview:")
        print(f"     Destination         : {overview.get('destination')}")
        print(f"     Dates               : {overview.get('start_date')} → {overview.get('end_date')}")
        print(f"     Total days          : {overview.get('total_days')}")
        print(f"     Group size          : {overview.get('group_size')} people")
        print(f"     Budget              : {overview.get('travel_budget', 0):,} VNĐ")
        print(f"     Estimated cost      : {overview.get('total_estimated_cost', 0):,} VNĐ")
        print(f"     Budget utilization  : {overview.get('budget_utilization_pct', 0):.1f}%")
        print(f"     Total activities    : {overview.get('total_activities', 0)}")

        highlights = overview.get("highlights", [])
        if highlights:
            print(f"\n  🌟 Highlights:")
            for h in highlights:
                print(f"     • {h}")

    except Exception as e:
        print(f"\n  ❌ Generate_answer FAILED: {e}")
        import traceback; traceback.print_exc()
        return False

    # ──────────────────────────────────────────────────────────────────────────
    # STEP 5: Final JSON dump
    # ──────────────────────────────────────────────────────────────────────────
    section("STEP 5: Full JSON Output (final_answer)")

    print(json_preview(state.get("final_answer", {}), max_chars=3000))

    return True


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        success = run_full_pipeline()
    except KeyboardInterrupt:
        print("\n\n⏹️  Interrupted by user")
        success = False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback; traceback.print_exc()
        success = False

    print(f"\n{DIVIDER}")
    if success:
        print("✅ FULL PIPELINE INTEGRATION TEST PASSED")
    else:
        print("❌ FULL PIPELINE INTEGRATION TEST FAILED")
    print(DIVIDER)

    sys.exit(0 if success else 1)
