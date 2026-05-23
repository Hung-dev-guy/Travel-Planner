import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Add the backend root directory to sys.path to ensure "workflow" package can be imported
backend_dir = Path(__file__).resolve().parents[2]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

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
    from workflow.nodes.Extractor_agent import extractor_node, extractor_chain
    print("✅ Successfully imported extractor_node and extractor_chain from Extractor_agent.py.")
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Ensure you are running the script from the 'backend' directory or that 'backend' is in your PYTHONPATH.")
    exit(1)


def test_extractor_chain(user_input: str):
    """
    Test the extractor langchain chain directly.
    """
    print(f"\n--- Testing Extractor Chain directly with input: '{user_input}' ---")
    try:
        response = extractor_chain.invoke({"user_input": user_input})
        # response is an ExtractorOutput BaseModel
        print("Success! Response from LLM:")
        print(json.dumps(response.model_dump(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Failed to invoke chain: {e}")

def test_extractor_node(inputs: dict):
    """
    Test the extractor node as it would be executed inside a LangGraph workflow.
    """
    print(f"\n--- Testing extractor_node with structured input state ---")
    mock_state = {
        "user_des_input": inputs.get("usr_des_input"),
        "usr_des_input": inputs.get("usr_des_input"),
        "group_size": inputs.get("group_size"),
        "start_date": inputs.get("start_date"),
        "end_date": inputs.get("end_date"),
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
            "usr_des_input": "Tôi muốn đi du lịch Đà Nẵng 3 ngày 2 đêm. Ngân sách khoảng 15 triệu, đi thong thả, thích ăn hải sản và ở khách sạn gần biển. Gia đình tôi có người già nên sẽ đi bộ ít thôi. Đứa con 5 tuổi của tôi không ăn được cay và dị ứng hải sản",
            "group_size": 4,
            "start_date": "2026-06-15",
            "end_date": "2026-06-18",
            "destination": ["Đà Nẵng", "Hội An"],
            "personal_travel_style_des": "Thích trải nghiệm văn hoá, không khí yên bình"
        },
    ]
    
    for i, inputs in enumerate(sample_inputs, 1):
        print("=" * 60)
        test_extractor_node(inputs)

