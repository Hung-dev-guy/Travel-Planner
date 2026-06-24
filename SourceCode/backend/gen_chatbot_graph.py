import sys
import os

# Set fake API key to bypass initialization
os.environ["GOOGLE_API_KEY"] = "fake-key"

sys.path.append("/home/hungdvlper/Documents/TTCS/Traplanner/SourceCode/backend")

from langchain_google_genai import ChatGoogleGenerativeAI
from chatbot.agent import create_agent_graph

# Initialize graph with a generic chat model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
graph = create_agent_graph(llm)

# Generate the mermaid PNG
try:
    png_data = graph.get_graph().draw_mermaid_png()
    output_path = "/home/hungdvlper/Documents/TTCS/Traplanner/SourceCode/backend/chatbot_mermaid.png"
    with open(output_path, "wb") as f:
        f.write(png_data)
    print(f"Successfully saved Mermaid PNG to {output_path}")
except Exception as e:
    print(f"Failed to draw mermaid PNG: {e}")
