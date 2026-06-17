import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, "../../../.."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Load environment variables
load_dotenv()

# Verify GOOGLE_API_KEY is available
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ Error: GOOGLE_API_KEY not found in environment or .env file.")
    exit(1)
else:
    print("✅ GOOGLE_API_KEY loaded successfully.")

# Import workflow nodes
try:
    from workflow.nodes.Extractor_agent import extractor_node
    print("✅ Successfully imported extractor_node from Extractor_agent.py.")
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Ensure you are running the script from the 'backend' directory or that 'backend' is in your PYTHONPATH.")
    exit(1)

def test_extractor_node(inputs: dict):
    """
    Test the extractor node as it would be executed inside a LangGraph workflow.
    """
    print(f"\n--- Testing extractor_node with structured input state ---")
    mock_state = {
        "user_des_input": inputs.get("user_des_input"),
        "usr_des_input": inputs.get("user_des_input"),
        "group_size": inputs.get("group_size"),
        "start_date": inputs.get("start_date"),
        "end_date": inputs.get("end_date"),
        "start_location": inputs.get("start_location"),
        "destination": inputs.get("destination"),
        "personal_travel_style_des": inputs.get("personal_travel_style_des"),
        "trip_metadata": {},
        "travel_preferences": {},
        "constraints": {}
    }
    
    try:
        new_state = extractor_node(mock_state)
        print("Success! New state returned by node:")
        print(json.dumps(new_state, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Failed to run extractor_node: {e}")

if __name__ == "__main__":
    # Sample inputs conforming to the new node structure
    sample_inputs = [
        {
            "user_des_input": "Mình muốn đi chill gần biển, ăn hải sản ngon và ngắm cảnh đẹp. Nhưng gia đình có người già hạn chế đi bộ, con 5 tuổi dị ứng hải sản và không ăn cay.",
            "group_size": 4,
            "start_date": "2026-06-15",
            "end_date": "2026-06-18",
            "start_location": "Nam Định, Ninh Bình",
            "destination": ["Kỳ Lừa, Lạng Sơn", "Hạ Long, Quảng Ninh"],
            "personal_travel_style_des": "Phong cách: nature, cultural. Nhịp độ: moderate. Đối tượng đi cùng: Family."
        },
    ]
    
    for i, inputs in enumerate(sample_inputs, 1):
        print("=" * 60)
        test_extractor_node(inputs)

