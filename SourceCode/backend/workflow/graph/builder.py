from typing import Literal
from workflow.graph.stage import State
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from workflow.nodes.Extractor_agent import extractor_node
from workflow.nodes.Mobility_agent import mobility_node
from workflow.nodes.Planner import Planner_node
from workflow.nodes.Scheduler import scheduling_node
from workflow.nodes.Validation_agent import validation_agent
from workflow.nodes.Generate_answer import generate_answer_node


# ──────────────────────────────────────────────────────────────────────────────
# Validation feedback-loop router
# ──────────────────────────────────────────────────────────────────────────────

MAX_VALIDATION_ITERATIONS = 3
MIN_ACCEPTABLE_SCORE = 70.0


def route_after_validation(state: State) -> Literal["planner", "mobility", "scheduling", "generate_answer"]:
    """
    Conditional routing after the validation node.

    Rules (priority order):
    1. Score ≥ MIN_ACCEPTABLE_SCORE  → proceed to generate_answer  ✅
    2. Iteration ≥ MAX_ITERATIONS    → proceed to generate_answer  ⚠️
    3. Score < MIN_ACCEPTABLE_SCORE  → loop back to scheduling     🔄
    """
    validation = state.get("validation", {})
    overall_score = validation.get("overall_score", 0)
    issues = validation.get("issues", [])
    iteration = state.get("validation_iteration", 1)

    if overall_score >= MIN_ACCEPTABLE_SCORE:
        return "generate_answer"

    if iteration >= MAX_VALIDATION_ITERATIONS:
        return "generate_answer"

    # Phân tích lỗi để điều hướng về đúng Node
    issues_str = " ".join([str(i) for i in issues]).lower()
    
    if "địa điểm" in issues_str or "ngân sách" in issues_str or "place" in issues_str or "budget" in issues_str:
        return "planner"
        
    if "di chuyển" in issues_str or "khoảng cách" in issues_str or "phương tiện" in issues_str or "route" in issues_str or "distance" in issues_str:
        return "mobility"

    return "scheduling"


# ──────────────────────────────────────────────────────────────────────────────
# Graph builder
# ──────────────────────────────────────────────────────────────────────────────

def build_workflow():
    workflow = StateGraph(State)

    # ── Register all nodes ─────────────────────────────────────────────────────
    workflow.add_node("extractor",       extractor_node)
    workflow.add_node("planner",         Planner_node)
    workflow.add_node("mobility",        mobility_node)
    workflow.add_node("scheduling",      scheduling_node)
    workflow.add_node("validation",      validation_agent)
    workflow.add_node("generate_answer", generate_answer_node)

    # ── Define the pipeline ────────────────────────────────────────────────────
    workflow.set_entry_point("extractor")
    workflow.add_edge("extractor",  "planner")
    workflow.add_edge("planner",    "mobility")
    workflow.add_edge("mobility",   "scheduling")

    # Validation feedback loop: scheduling → validation → (planner | mobility | scheduling | generate_answer)
    workflow.add_edge("scheduling", "validation")
    workflow.add_conditional_edges(
        "validation",
        route_after_validation,
        {
            "planner":         "planner",
            "mobility":        "mobility",
            "scheduling":      "scheduling",
            "generate_answer": "generate_answer",
        },
    )
    workflow.add_edge("generate_answer", END)

    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)
