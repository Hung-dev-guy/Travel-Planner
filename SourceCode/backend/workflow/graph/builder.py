from typing import Literal
from workflow.graph.stage import State
from langgraph.graph import StateGraph, END
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


def _route_after_validation(state: State) -> Literal["scheduling", "generate_answer"]:
    """
    Conditional routing after the validation node.

    Rules (priority order):
    1. Score ≥ MIN_ACCEPTABLE_SCORE  → proceed to generate_answer  ✅
    2. Iteration ≥ MAX_ITERATIONS    → proceed to generate_answer  ⚠️
    3. Score < MIN_ACCEPTABLE_SCORE  → loop back to scheduling     🔄
    """
    validation = state.get("validation", {})
    overall_score = validation.get("overall_score", 0)
    iteration = state.get("validation_iteration", 1)

    if overall_score >= MIN_ACCEPTABLE_SCORE:
        return "generate_answer"

    if iteration >= MAX_VALIDATION_ITERATIONS:
        return "generate_answer"

    # Prepare state for next iteration
    state["validation_iteration"] = iteration + 1

    # Pass recommendations as feedback to the scheduler
    recommendations = validation.get("recommendations", [])
    if recommendations:
        # Convert recommendation dicts (already serialised by to_dict()) back to list
        state["validation_feedback"] = [
            r if isinstance(r, dict) else r.to_dict()
            for r in recommendations
        ]

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

    # Validation feedback loop: scheduling → validation → (scheduling | generate_answer)
    workflow.add_edge("scheduling", "validation")
    workflow.add_conditional_edges(
        "validation",
        _route_after_validation,
        {
            "scheduling":      "scheduling",
            "generate_answer": "generate_answer",
        },
    )
    workflow.add_edge("generate_answer", END)

    return workflow.compile()
