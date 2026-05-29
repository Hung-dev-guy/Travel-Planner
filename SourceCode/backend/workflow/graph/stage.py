# src/graph/stage.py
from typing import List, Dict, TypedDict, Any, Optional

class TripMetadata(TypedDict):
    usr_des: str 
    start_date: str 
    end_date: str
    total_days: str 
    age_range: str 
    start_location: str
    destination: str 
    
class TravelPreferences(TypedDict):
    travel_style: List[str]
    travel_pace: List[str]
    food_style: List[str]
    accommodation_style: List[str]
    mobility_style: List[str]
    atmosphere: List[str] 
    companion_type: List[str]
    
class Constraints(TypedDict):
    travel_budget: int 
    group_size: int 
    daily_active_hours: Optional[str] 
    language: Optional[str] 
    max_radius_distance: Optional[int]
    places_of_limitation: Optional[List[str]]
    health_limitations: Optional[List[str]]
    mobility_limitations: Optional[List[str]]    

class State(TypedDict):
    # Initial input fields
    user_des_input: Optional[str]
    group_size: Optional[int]
    start_date: Optional[str]
    end_date: Optional[str]
    start_location: Optional[str]
    destination: Optional[List[str]]
    personal_travel_style_des: Optional[str]

    # Node output / structured fields
    trip_metadata: TripMetadata
    travel_preferences: TravelPreferences
    constraints: Constraints

    activities: List[Dict[str, Any]]
    accommodations: List[Dict[str, Any]]
    transportations: List[Dict[str, Any]]
    scheduling: List[Dict[str, Any]]

    # Validation fields
    validation: Optional[Dict[str, Any]]           # ValidationResult.to_dict() output
    validation_feedback: Optional[List[Dict]]      # Recommendations passed back to Scheduler
    validation_iteration: Optional[int]            # Tracks the current feedback loop iteration
    final_answer: Optional[Dict[str, Any]]         # Final formatted output from Generate_answer