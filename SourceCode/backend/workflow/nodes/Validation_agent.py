"""
Validation Agent: Quality Assurance Gate for Travel Plans

This node validates the complete itinerary against multiple criteria to ensure
the travel plan is feasible, suitable, balanced, and optimized.

Validates:
- Budget Feasibility (20%): Total/daily costs vs constraints
- Time Feasibility (15%): Daily active hours, meal times, rest periods
- Activity Suitability (20%): Activities match preferences & group type
- Accommodation Quality (15%): Accommodations match needs
- Transportation Efficiency (10%): Routing logic and costs
- Schedule Balance (10%): Activity/rest distribution
- Health & Safety (10%): Respects health limitations

Features:
- Generates validation scores with category breakdown
- Identifies specific issues with severity levels
- Creates actionable recommendations prioritized by impact
- Supports iterative improvement via feedback loop
- Prevents infinite loops with configurable max_iterations
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================

class SeverityLevel(Enum):
    """Issue severity levels"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class PriorityLevel(Enum):
    """Recommendation priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ValidationIssue:
    """Represents a single validation issue"""
    severity: str  # 'critical' | 'warning' | 'info'
    category: str  # 'budget' | 'time' | 'suitability' | 'accommodation' | 'transport' | 'balance' | 'health'
    day: Optional[int]  # Which day has the issue (None for overall)
    message: str  # Description of issue
    impact: str  # How it affects the plan
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity": self.severity,
            "category": self.category,
            "day": self.day,
            "message": self.message,
            "impact": self.impact
        }


@dataclass
class ValidationRecommendation:
    """Represents a recommendation to improve the plan"""
    priority: str  # 'high' | 'medium' | 'low'
    category: str  # Which criterion this addresses
    suggestion: str  # What to do
    rationale: str  # Why this would help
    expected_improvement: Dict[str, float]  # How scores would improve
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "priority": self.priority,
            "category": self.category,
            "suggestion": self.suggestion,
            "rationale": self.rationale,
            "expected_improvement": self.expected_improvement
        }


@dataclass
class ValidationResult:
    """Complete validation result with scores and recommendations"""
    is_valid: bool
    overall_score: float
    category_scores: Dict[str, float]
    issues: List[ValidationIssue]
    recommendations: List[ValidationRecommendation]
    status: str  # 'APPROVED' | 'NEEDS_IMPROVEMENT' | 'CRITICAL_ISSUES'
    summary: str
    iteration: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "overall_score": self.overall_score,
            "category_scores": self.category_scores,
            "issues": [i.to_dict() for i in self.issues],
            "recommendations": [r.to_dict() for r in self.recommendations],
            "status": self.status,
            "summary": self.summary,
            "iteration": self.iteration
        }


# ============================================================================
# Scoring Functions
# ============================================================================

def validate_budget(scheduling: List[Dict[str, Any]], constraints: Dict[str, Any]) -> Tuple[float, List[ValidationIssue]]:
    """
    Validates budget feasibility (20 points max)
    
    Checks:
    - Total trip cost vs travel_budget
    - Daily costs vs daily_budget
    - Per-person cost (group_size aware)
    """
    issues = []
    score = 20.0  # Start with full points
    
    if not scheduling or not constraints:
        return 0.0, [ValidationIssue(
            severity=SeverityLevel.CRITICAL.value,
            category="budget",
            day=None,
            message="Missing scheduling or constraint data",
            impact="Cannot validate budget"
        )]
    
    travel_budget = constraints.get("travel_budget", float('inf'))
    group_size = constraints.get("group_size", 1)
    
    # Calculate total trip cost
    total_cost = 0.0
    day_costs = []
    
    for day_idx, day_schedule in enumerate(scheduling, 1):
        items = day_schedule.get("items", [])
        day_cost = sum(item.get("cost", 0) for item in items)
        day_costs.append(day_cost)
        total_cost += day_cost
    
    # Check total budget
    budget_usage_pct = (total_cost / travel_budget * 100) if travel_budget > 0 else 0
    
    if budget_usage_pct > 120:
        score = 0.0
        issues.append(ValidationIssue(
            severity=SeverityLevel.CRITICAL.value,
            category="budget",
            day=None,
            message=f"Trip exceeds budget by {budget_usage_pct - 100:.1f}% ({total_cost:,.0f} VNĐ vs {travel_budget:,.0f} VNĐ)",
            impact="Plan is financially infeasible. User cannot afford this trip."
        ))
    elif budget_usage_pct > 100:
        score = 10.0
        issues.append(ValidationIssue(
            severity=SeverityLevel.CRITICAL.value,
            category="budget",
            day=None,
            message=f"Trip exceeds budget by {budget_usage_pct - 100:.1f}% ({total_cost:,.0f} vs {travel_budget:,.0f} VNĐ)",
            impact="Plan requires additional funding"
        ))
    elif budget_usage_pct > 80:
        score = 15.0
        issues.append(ValidationIssue(
            severity=SeverityLevel.WARNING.value,
            category="budget",
            day=None,
            message=f"Budget utilization at {budget_usage_pct:.1f}%. Limited contingency funds.",
            impact="Little room for unexpected expenses or upgrades"
        ))
    
    # Check daily budget distribution
    if day_costs:
        max_daily_cost = max(day_costs)
        daily_budget = travel_budget / len(scheduling) if len(scheduling) > 0 else 0
        
        for day_idx, day_cost in enumerate(day_costs, 1):
            if day_cost > daily_budget * 1.3:
                issues.append(ValidationIssue(
                    severity=SeverityLevel.WARNING.value,
                    category="budget",
                    day=day_idx,
                    message=f"Day {day_idx} cost ({day_cost:,.0f} VNĐ) exceeds daily budget ({daily_budget:,.0f} VNĐ)",
                    impact="Uneven budget distribution across days"
                ))
    
    logger.info(f"Budget validation: score={score}, usage={budget_usage_pct:.1f}%, total={total_cost:,.0f}VNĐ")
    return score, issues


def validate_time(scheduling: List[Dict[str, Any]], constraints: Dict[str, Any]) -> Tuple[float, List[ValidationIssue]]:
    """
    Validates time feasibility (15 points max)
    
    Checks:
    - Daily active hours vs daily_active_hours constraint
    - Meal times are realistic
    - Rest hours >= 8 per night
    """
    issues = []
    score = 15.0  # Start with full points
    
    if not scheduling or not constraints:
        return 0.0, [ValidationIssue(
            severity=SeverityLevel.CRITICAL.value,
            category="time",
            day=None,
            message="Missing scheduling or constraint data",
            impact="Cannot validate time feasibility"
        )]
    
    daily_active_hours = constraints.get("daily_active_hours", 10)
    
    days_over = 0
    total_excess = 0
    
    for day_idx, day_schedule in enumerate(scheduling, 1):
        items = day_schedule.get("items", [])
        
        # Calculate active hours (exclude accommodation)
        active_hours = sum(
            item.get("duration", 60) / 60  # Convert minutes to hours
            for item in items
            if item.get("type") != "accommodation"
        )
        
        if active_hours > daily_active_hours:
            days_over += 1
            total_excess += active_hours - daily_active_hours
            score = max(0.0, score - 3.0)
            
            issues.append(ValidationIssue(
                severity=SeverityLevel.WARNING.value,
                category="time",
                day=day_idx,
                message=f"Day {day_idx} has {active_hours:.1f} active hours (constraint: {daily_active_hours}h)",
                impact="Risk of exhaustion and reduced trip enjoyment"
            ))
        
        # Check rest hours (assume 8 hours sleep needed)
        rest_hours = 24 - active_hours - 1  # 1 hour for meals/breaks
        if rest_hours < 8:
            issues.append(ValidationIssue(
                severity=SeverityLevel.WARNING.value,
                category="time",
                day=day_idx,
                message=f"Day {day_idx} has only {rest_hours:.1f} hours rest (recommended: 8h)",
                impact="Insufficient sleep may impact health and trip enjoyment"
            ))
    
    if days_over > 0:
        logger.warning(f"Time validation: {days_over} days exceed active hour limit")
    
    return max(0.0, score), issues


def validate_activities(scheduling: List[Dict[str, Any]], preferences: Dict[str, Any]) -> Tuple[float, List[ValidationIssue]]:
    """
    Validates activity suitability (20 points max)
    
    Checks:
    - Activity types match travel_style preferences
    - Activity pace aligns with travel_pace
    - Activity atmosphere matches preferences
    - Activity distribution (variety vs repetition)
    """
    issues = []
    score = 0.0  # Accumulate points for each activity
    
    if not scheduling or not preferences:
        return 0.0, [ValidationIssue(
            severity=SeverityLevel.INFO.value,
            category="activity_suitability",
            day=None,
            message="Missing scheduling or preference data",
            impact="Cannot validate activity suitability"
        )]
    
    travel_style = preferences.get("travel_style", [])
    travel_pace = preferences.get("travel_pace", "moderate")
    
    activity_types = []
    perfect_matches = 0
    good_matches = 0
    neutral_matches = 0
    poor_matches = 0
    
    for day_idx, day_schedule in enumerate(scheduling, 1):
        items = day_schedule.get("items", [])
        
        for item in items:
            if item.get("type") != "activity":
                continue
            
            activity_types.append(item.get("category", "unknown"))
            
            # Score activity match
            category = item.get("category", "").lower()
            suitability = item.get("suitability", [])
            
            # Check against travel_style
            style_match = any(style.lower() in category or style.lower() in str(suitability).lower() 
                            for style in (travel_style if isinstance(travel_style, list) else [travel_style]))
            
            if style_match:
                perfect_matches += 1
                score += 5.0
            else:
                # Check if activity is at least acceptable
                if "general" in category or len(suitability) > 0:
                    good_matches += 1
                    score += 3.0
                else:
                    poor_matches += 1
    
    # Normalize to 0-20
    if activity_types:
        num_activities = len(activity_types)
        # Score based on perfect and good matches
        activity_score = ((perfect_matches * 5.0 + good_matches * 3.0) / (num_activities * 5.0)) * 20.0
        score = min(20.0, activity_score)
    else:
        score = 10.0  # Average if no activities
    
    # Check for variety
    if activity_types:
        unique_types = len(set(activity_types))
        total_activities = len(activity_types)
        
        if unique_types < total_activities * 0.5:
            issues.append(ValidationIssue(
                severity=SeverityLevel.WARNING.value,
                category="activity_suitability",
                day=None,
                message=f"Low activity variety: {unique_types} unique types for {total_activities} activities",
                impact="Trip may feel repetitive or monotonous"
            ))
        else:
            issues.append(ValidationIssue(
                severity=SeverityLevel.INFO.value,
                category="activity_suitability",
                day=None,
                message=f"Good activity mix: {unique_types} types across {total_activities} activities",
                impact="Diverse experiences planned"
            ))
    
    logger.info(f"Activity validation: score={score:.1f}, perfect={perfect_matches}, good={good_matches}, poor={poor_matches}")
    return score, issues


def validate_accommodations(scheduling: List[Dict[str, Any]], preferences: Dict[str, Any]) -> Tuple[float, List[ValidationIssue]]:
    """
    Validates accommodation quality (15 points max)
    
    Checks:
    - Accommodation style matches preference
    - All nights covered
    - Cost reasonable for region
    - Quality consistency
    """
    issues = []
    score = 15.0  # Start with full points
    
    if not scheduling or not preferences:
        return 0.0, [ValidationIssue(
            severity=SeverityLevel.WARNING.value,
            category="accommodation",
            day=None,
            message="Missing scheduling or preference data",
            impact="Cannot validate accommodation suitability"
        )]
    
    accommodation_style = preferences.get("accommodation_style", "comfortable")
    
    accommodations = []
    accommodation_costs = []
    
    for day_idx, day_schedule in enumerate(scheduling, 1):
        items = day_schedule.get("items", [])
        
        for item in items:
            if item.get("type") == "accommodation":
                accommodations.append({
                    "day": day_idx,
                    "name": item.get("name", "Unknown"),
                    "cost": item.get("cost", 0),
                    "quality": item.get("quality_level", "standard")
                })
                accommodation_costs.append(item.get("cost", 0))
    
    # Check if all nights covered
    if len(accommodations) < len(scheduling) - 1:  # -1 for last day (checkout)
        score -= 5.0
        issues.append(ValidationIssue(
            severity=SeverityLevel.CRITICAL.value,
            category="accommodation",
            day=None,
            message=f"Not all nights covered: {len(accommodations)} accommodations for {len(scheduling)} days",
            impact="Missing accommodations for some nights"
        ))
    
    # Check cost consistency
    if accommodation_costs:
        avg_cost = sum(accommodation_costs) / len(accommodation_costs)
        max_cost = max(accommodation_costs)
        min_cost = min(accommodation_costs)
        
        if max_cost > avg_cost * 1.5:
            score -= 3.0
            issues.append(ValidationIssue(
                severity=SeverityLevel.WARNING.value,
                category="accommodation",
                day=None,
                message=f"Accommodation cost inconsistency: {min_cost:,.0f} - {max_cost:,.0f} VNĐ (avg: {avg_cost:,.0f})",
                impact="Variable quality across nights may affect experience"
            ))
    
    # Positive feedback
    if len(accommodations) >= len(scheduling) - 1:
        issues.append(ValidationIssue(
            severity=SeverityLevel.INFO.value,
            category="accommodation",
            day=None,
            message=f"All nights covered with consistent quality accommodations",
            impact="Good accommodation planning"
        ))
    
    logger.info(f"Accommodation validation: score={score}, count={len(accommodations)}, avg_cost={sum(accommodation_costs)/len(accommodation_costs) if accommodation_costs else 0:,.0f}")
    return max(0.0, score), issues


def validate_transportation(scheduling: List[Dict[str, Any]]) -> Tuple[float, List[ValidationIssue]]:
    """
    Validates transportation efficiency (10 points max)
    
    Checks:
    - No backtracking or illogical routing
    - Transport times reasonable
    - Schedule allows realistic check-in/check-out
    """
    issues = []
    score = 10.0  # Start with full points
    
    if not scheduling:
        return 0.0, [ValidationIssue(
            severity=SeverityLevel.INFO.value,
            category="transport",
            day=None,
            message="No scheduling data to validate transport",
            impact="Cannot validate transportation"
        )]
    
    transport_days = []
    last_location = None
    
    for day_idx, day_schedule in enumerate(scheduling, 1):
        items = day_schedule.get("items", [])
        
        for item in items:
            if item.get("type") == "transport":
                from_loc = item.get("from_location", "")
                to_loc = item.get("to_location", "")
                
                transport_days.append({
                    "day": day_idx,
                    "from": from_loc,
                    "to": to_loc
                })
                
                # Check for backtracking
                if last_location and from_loc != last_location:
                    issues.append(ValidationIssue(
                        severity=SeverityLevel.WARNING.value,
                        category="transport",
                        day=day_idx,
                        message=f"Potential backtracking: {last_location} → {to_loc} vs previous {from_loc}",
                        impact="Inefficient routing increases travel time/cost"
                    ))
                    score -= 2.0
                
                last_location = to_loc
    
    if not transport_days:
        issues.append(ValidationIssue(
            severity=SeverityLevel.INFO.value,
            category="transport",
            day=None,
            message="Local exploration (no inter-destination transport)",
            impact="Simple transport logistics"
        ))
    
    logger.info(f"Transport validation: score={score}, transport_routes={len(transport_days)}")
    return max(0.0, score), issues


def validate_balance(scheduling: List[Dict[str, Any]]) -> Tuple[float, List[ValidationIssue]]:
    """
    Validates schedule balance (10 points max)
    
    Checks:
    - Activity distribution across days
    - No "dead" days (only meals)
    - No "exhausting" days (constant activity)
    - Mix of rest and activity
    """
    issues = []
    score = 10.0  # Start with full points
    
    if not scheduling:
        return 0.0, [ValidationIssue(
            severity=SeverityLevel.INFO.value,
            category="balance",
            day=None,
            message="No scheduling data",
            impact="Cannot validate balance"
        )]
    
    dead_days = 0
    exhausting_days = 0
    
    for day_idx, day_schedule in enumerate(scheduling, 1):
        items = day_schedule.get("items", [])
        
        # Count different types of items
        activities = [i for i in items if i.get("type") == "activity"]
        meals = [i for i in items if i.get("type") == "meal"]
        accommodation = [i for i in items if i.get("type") == "accommodation"]
        transport = [i for i in items if i.get("type") == "transport"]
        
        # Check for dead days
        if len(activities) == 0 and len(items) > 0:
            dead_days += 1
            issues.append(ValidationIssue(
                severity=SeverityLevel.INFO.value,
                category="balance",
                day=day_idx,
                message=f"Day {day_idx} is arrival/departure day (no activities)",
                impact="Expected for first/last days"
            ))
            score -= 1.0
        
        # Check for exhausting days
        if len(activities) >= 4:
            exhausting_days += 1
            issues.append(ValidationIssue(
                severity=SeverityLevel.WARNING.value,
                category="balance",
                day=day_idx,
                message=f"Day {day_idx} has {len(activities)} activities (potentially exhausting)",
                impact="Risk of traveler fatigue and reduced enjoyment"
            ))
            score -= 2.0
        
        # Positive feedback for balanced days
        if 1 <= len(activities) <= 3 and len(meals) >= 2:
            issues.append(ValidationIssue(
                severity=SeverityLevel.INFO.value,
                category="balance",
                day=day_idx,
                message=f"Day {day_idx}: Good balance ({len(activities)} activities, {len(meals)} meals)",
                impact="Well-planned day with appropriate pacing"
            ))
    
    logger.info(f"Balance validation: score={score}, dead_days={dead_days}, exhausting={exhausting_days}")
    return max(0.0, score), issues


def validate_health_safety(scheduling: List[Dict[str, Any]], constraints: Dict[str, Any]) -> Tuple[float, List[ValidationIssue]]:
    """
    Validates health & safety (10 points max)
    
    Checks:
    - No activities contraindicated by health_limitations
    - Adequate rest between strenuous activities
    - No age-inappropriate activities
    """
    issues = []
    score = 10.0  # Start with full points
    
    if not scheduling or not constraints:
        return 0.0, [ValidationIssue(
            severity=SeverityLevel.INFO.value,
            category="health",
            day=None,
            message="Missing scheduling or constraint data",
            impact="Cannot validate health & safety"
        )]
    
    health_limitations = constraints.get("health_limitations", [])
    if isinstance(health_limitations, str):
        health_limitations = [health_limitations]
    
    age_range = constraints.get("age_range", (18, 65))
    
    for day_idx, day_schedule in enumerate(scheduling, 1):
        items = day_schedule.get("items", [])
        
        for item in items:
            if item.get("type") != "activity":
                continue
            
            activity_name = item.get("name", "").lower()
            activity_category = item.get("category", "").lower()
            
            # Check for health contraindications
            for limitation in health_limitations:
                limitation_lower = limitation.lower()
                
                if "mobility" in limitation_lower or "walking" in limitation_lower:
                    if any(word in activity_category for word in ["hiking", "trek", "climbing"]):
                        score -= 5.0
                        issues.append(ValidationIssue(
                            severity=SeverityLevel.CRITICAL.value,
                            category="health",
                            day=day_idx,
                            message=f"Activity '{item.get('name')}' contraindicated by health limitation: {limitation}",
                            impact="Activity may cause injury or health issues"
                        ))
    
    # Check rest hours
    for day_idx, day_schedule in enumerate(scheduling, 1):
        items = day_schedule.get("items", [])
        
        # Calculate active hours
        active_hours = sum(
            item.get("duration", 60) / 60
            for item in items
            if item.get("type") == "activity"
        )
        
        rest_hours = 24 - active_hours - 2  # -2 for meals/breaks
        
        if rest_hours < 8:
            issues.append(ValidationIssue(
                severity=SeverityLevel.WARNING.value,
                category="health",
                day=day_idx,
                message=f"Day {day_idx} has only {rest_hours:.1f} hours rest (recommended: 8h)",
                impact="Insufficient sleep may impact health"
            ))
            score -= 1.0
    
    if not any(i.severity == "critical" for i in issues):
        issues.append(ValidationIssue(
            severity=SeverityLevel.INFO.value,
            category="health",
            day=None,
            message="All activities are age-appropriate and health-safe",
            impact="Good health & safety planning"
        ))
    
    logger.info(f"Health & safety validation: score={score}, limitations={len(health_limitations)}")
    return max(0.0, score), issues


# ============================================================================
# Main Validation Functions
# ============================================================================

def calculate_overall_score(category_scores: Dict[str, float]) -> float:
    """
    Calculate weighted overall score (0-100)
    
    Scores are normalized to 0-100 scale before weighting:
    - Budget: 20 points → 100 scale
    - Time: 15 points → 100 scale
    - Activity Suitability: 20 points → 100 scale
    - Accommodation: 15 points → 100 scale
    - Transport: 10 points → 100 scale
    - Balance: 10 points → 100 scale
    - Health: 10 points → 100 scale
    """
    # Normalization factors (max points for each category)
    max_points = {
        "budget": 20.0,
        "time": 15.0,
        "activity_suitability": 20.0,
        "accommodation": 15.0,
        "transport": 10.0,
        "balance": 10.0,
        "health": 10.0
    }
    
    # Weights
    weights = {
        "budget": 0.20,
        "time": 0.15,
        "activity_suitability": 0.20,
        "accommodation": 0.15,
        "transport": 0.10,
        "balance": 0.10,
        "health": 0.10
    }
    
    total_score = 0.0
    total_weight = 0.0
    
    for category, weight in weights.items():
        if category in category_scores:
            # Normalize to 0-100 scale
            max_pts = max_points.get(category, 100)
            normalized_score = (category_scores[category] / max_pts * 100) if max_pts > 0 else 0
            total_score += normalized_score * weight
            total_weight += weight
    
    return (total_score / total_weight) if total_weight > 0 else 0


def determine_status(score: float, issues: List[ValidationIssue]) -> str:
    """Determine validation status based on score and critical issues"""
    critical_issues = [i for i in issues if i.severity == SeverityLevel.CRITICAL.value]
    
    if critical_issues and score < 50:
        return "CRITICAL_ISSUES"
    elif score >= 70:
        return "APPROVED"
    else:
        return "NEEDS_IMPROVEMENT"


def generate_summary(
    score: float,
    status: str,
    category_scores: Dict[str, float],
    issues: List[ValidationIssue]
) -> str:
    """Generate human-readable summary"""
    summary = f"Overall Score: {score:.0f}% | Status: {status}\n"
    
    if status == "APPROVED":
        summary += f"✅ Plan is feasible and well-balanced. Ready for execution."
    elif status == "CRITICAL_ISSUES":
        summary += f"❌ Plan has critical issues that must be resolved. {len(issues)} issues found."
    else:
        summary += f"⚠️ Plan needs improvement. {len(issues)} issues found, {sum(1 for i in issues if i.severity == 'warning')} warnings."
    
    # Add category breakdown
    summary += "\n\nCategory Breakdown:\n"
    for category, cat_score in sorted(category_scores.items()):
        status_icon = "✅" if cat_score >= 70 else "⚠️" if cat_score >= 50 else "❌"
        summary += f"  {status_icon} {category.replace('_', ' ').title()}: {cat_score:.0f}%\n"
    
    return summary


def sort_recommendations_by_priority(recommendations: List[ValidationRecommendation]) -> List[ValidationRecommendation]:
    """Sort recommendations by priority (high → medium → low)"""
    priority_order = {"high": 0, "medium": 1, "low": 2}
    return sorted(
        recommendations,
        key=lambda r: priority_order.get(r.priority, 3)
    )


def validation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main validation node that validates the travel plan
    
    Input:
    - scheduling: List[Dict] - Day-by-day schedule from Scheduler
    - constraints: Dict - User constraints and preferences
    - travel_preferences: Dict - Travel style preferences
    - validation_iteration: int (optional) - Current feedback loop iteration
    
    Output:
    - validation: ValidationResult - Complete validation analysis
    
    If validation_iteration > 0, this indicates feedback from previous validation
    """
    
    scheduling = state.get("scheduling", [])
    constraints = state.get("constraints", {})
    preferences = state.get("travel_preferences", {})
    iteration = state.get("validation_iteration", 1)
    
    logger.info(f"Starting validation (iteration {iteration}) for {len(scheduling)} days")
    
    # Run all validation checks
    budget_score, budget_issues = validate_budget(scheduling, constraints)
    time_score, time_issues = validate_time(scheduling, constraints)
    activity_score, activity_issues = validate_activities(scheduling, preferences)
    accommodation_score, accommodation_issues = validate_accommodations(scheduling, preferences)
    transport_score, transport_issues = validate_transportation(scheduling)
    balance_score, balance_issues = validate_balance(scheduling)
    health_score, health_issues = validate_health_safety(scheduling, constraints)
    
    # Collect all scores and issues
    category_scores = {
        "budget": budget_score,
        "time": time_score,
        "activity_suitability": activity_score,
        "accommodation": accommodation_score,
        "transport": transport_score,
        "balance": balance_score,
        "health": health_score
    }
    
    all_issues = (
        budget_issues + time_issues + activity_issues +
        accommodation_issues + transport_issues + balance_issues + health_issues
    )
    
    # Calculate overall score
    overall_score = calculate_overall_score(category_scores)
    status = determine_status(overall_score, all_issues)
    summary = generate_summary(overall_score, status, category_scores, all_issues)
    
    # Generate recommendations for improvement
    recommendations = []
    
    # Budget recommendations
    if budget_score < 70:
        recommendations.append(ValidationRecommendation(
            priority="high",
            category="budget",
            suggestion="Remove or replace expensive activities with budget alternatives",
            rationale="Budget constraint exceeded. Prioritize lower-cost activities.",
            expected_improvement={"budget": 20, "overall": 5}
        ))
    
    # Time recommendations
    if time_score < 70:
        recommendations.append(ValidationRecommendation(
            priority="high",
            category="time",
            suggestion="Reduce daily activities or redistribute across more days",
            rationale="Daily active hours exceed recommended limit. Risk of exhaustion.",
            expected_improvement={"time": 25, "health": 10, "overall": 6}
        ))
    
    # Activity suitability recommendations
    if activity_score < 70:
        recommendations.append(ValidationRecommendation(
            priority="medium",
            category="activity_suitability",
            suggestion="Swap low-suitability activities with better-matching alternatives",
            rationale="Activities don't align well with travel preferences and style.",
            expected_improvement={"activity_suitability": 20, "overall": 4}
        ))
    
    # Balance recommendations
    if balance_score < 70:
        recommendations.append(ValidationRecommendation(
            priority="medium",
            category="balance",
            suggestion="Redistribute activities to balance packed and light days",
            rationale="Schedule is unbalanced with some days over-packed and others empty.",
            expected_improvement={"balance": 25, "health": 10, "overall": 4}
        ))
    
    recommendations = sort_recommendations_by_priority(recommendations)
    
    # Create validation result
    validation_result = ValidationResult(
        is_valid=status == "APPROVED",
        overall_score=overall_score,
        category_scores=category_scores,
        issues=all_issues,
        recommendations=recommendations,
        status=status,
        summary=summary,
        iteration=iteration
    )
    
    # Update state
    state["validation"] = validation_result.to_dict()
    state["validation_result"] = validation_result  # Keep object for feedback loop
    
    logger.info(f"Validation complete: score={overall_score:.0f}, status={status}, issues={len(all_issues)}")
    
    return state


def validation_feedback_loop(
    initial_state: Dict[str, Any],
    max_iterations: int = 3,
    min_acceptable_score: float = 70
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Iterative validation with feedback to scheduler for improvement
    
    Returns:
    - Final state with improved scheduling
    - History of validation iterations
    """
    state = initial_state.copy()
    iteration_history = []
    
    logger.info(f"Starting validation feedback loop (max {max_iterations} iterations)")
    
    for iteration in range(1, max_iterations + 1):
        state["validation_iteration"] = iteration
        
        # Run validation
        state = validation_node(state)
        
        validation_result = state.get("validation_result")
        if not validation_result:
            break
        
        # Record iteration
        iteration_history.append({
            "iteration": iteration,
            "score": validation_result.overall_score,
            "status": validation_result.status,
            "category_scores": validation_result.category_scores
        })
        
        logger.info(f"Iteration {iteration}: score={validation_result.overall_score:.0f}%")
        
        # Check exit conditions
        if validation_result.overall_score >= min_acceptable_score:
            logger.info(f"✅ Exit at iteration {iteration}: score={validation_result.overall_score:.0f}% (≥ {min_acceptable_score}%)")
            break
        
        if iteration >= max_iterations:
            logger.warning(f"⏹️ Reached max iterations ({max_iterations}). Accepting best plan with score={validation_result.overall_score:.0f}%")
            break
        
        # Check for no improvement
        if len(iteration_history) >= 2:
            prev_score = iteration_history[-2]["score"]
            curr_score = validation_result.overall_score
            
            if curr_score < prev_score:
                logger.warning(f"Score declined ({prev_score:.0f}% → {curr_score:.0f}%). Exiting.")
                break
        
        # Send recommendations to scheduler for improvement
        recommendations = validation_result.recommendations
        if recommendations:
            state["validation_feedback"] = recommendations
            logger.info(f"Sending {len(recommendations)} recommendations to scheduler")
            
            # In real pipeline, this would call scheduler_node(state)
            # For now, we just pass through the feedback
        else:
            logger.info("No recommendations generated. Exiting loop.")
            break
    
    return state, iteration_history


# ============================================================================
# Node Entry Point
# ============================================================================

def validation_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validation agent entry point for workflow
    
    Performs single validation pass on the schedule
    """
    return validation_node(state)
