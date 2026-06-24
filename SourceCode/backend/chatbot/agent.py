"""
chatbot/agent.py
LangGraph-based agentic travel advisor.

Graph flow:
  memory_init → classify_query
      ├─(no retrieval)→ direct_response → memory_save → END
      └─(retrieval)  → retrieve_trip_context → agent → [tool loop] → memory_save → END
"""

import logging
import operator
from typing import TypedDict, Annotated, Sequence, Optional, List
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from .prompts import TRAVEL_ADVISOR_SYSTEM_PROMPT, TRIP_CONTEXT_TEMPLATE
from .memory import MemoryManager
from .db import get_full_trip_context
from .tools import (
    get_trip_details,
    search_alternative_hotels,
    search_alternative_restaurants,
    search_alternative_attractions,
    search_transport_options,
    calculate_trip_budget,
    search_destination_info,
    summarize_conversation,
    classify_query_type,
    direct_response,
    update_trip_activity,
    update_transport_options,  
    add_new_activity,
    remove_activity,
)

logger = logging.getLogger(__name__)

ALL_TOOLS = [
    get_trip_details,
    search_alternative_hotels,
    search_alternative_restaurants,
    search_alternative_attractions,
    search_transport_options,
    calculate_trip_budget,
    search_destination_info,
    summarize_conversation,
    update_trip_activity,
    update_transport_options,
    add_new_activity,
    remove_activity,
]

# ── State ──────────────────────────────────────────────────────────────────────
class AgentState(TypedDict):
    """State shared across all nodes in the LangGraph."""
    input: str
    user_id: str
    trip_id: str        
    messages: Annotated[Sequence[BaseMessage], operator.add]
    trip_context: Optional[str]
    # Memory
    memory_manager: Optional[MemoryManager]
    short_term_memory: Optional[Sequence[BaseMessage]]
    conversation_summaries: Optional[list]
    # Classification
    needs_retrieval: Optional[bool]
    query_type: Optional[str]
    confidence: Optional[float]


# Graph factory 
def create_agent_graph(llm):
    """Build and compile the LangGraph travel advisor agent."""
    llm_with_tools = llm.bind_tools(ALL_TOOLS)
    # Node: memory_init 
    def memory_init_node(state: AgentState) -> dict:
        logger.info("[Node] memory_init")
        mm = MemoryManager.from_env()
        short_term = mm.load_short_term_memory(state["user_id"])
        summaries = mm.get_conversation_summaries(state["user_id"], limit=5)
        return {
            "memory_manager": mm,
            "short_term_memory": short_term,
            "conversation_summaries": summaries,
        }

    # Node: classify_query 
    def classify_query_node(state: AgentState) -> dict:
        logger.info(f"[Node] classify_query: '{state['input'][:80]}'")
        result = classify_query_type.invoke({"user_query": state["input"]})
        logger.info(f"  → {result}")
        return result

    # Node: retrieve_trip_context 
    def retrieve_trip_context_node(state: AgentState) -> dict:
        logger.info(f"[Node] retrieve_trip_context: trip_id={state.get('trip_id')}")
        trip_id = state.get("trip_id")
        if not trip_id:
            return {"trip_context": "Chưa chọn kế hoạch du lịch cụ thể."}

        try:
            ctx = get_full_trip_context(trip_id)
            if not ctx:
                return {"trip_context": f"Không tìm thấy kế hoạch du lịch ID: {trip_id}"}
            trip = ctx.get("trip", {})
            days = ctx.get("day_details", [])

            # Format day details concisely
            days_text = ""
            for day in days:
                day_num = day.get("dayNumber", "?")
                date_val = day.get("date", "")
                date_str = str(date_val)[:10] if date_val else ""
                days_text += f"\n  📅 Ngày {day_num} ({date_str}):\n"
                for act in day.get("dayActs", []):
                    name = act.get("name", "")
                    act_type = act.get("type", "")
                    start = str(act.get("startTime", ""))[-8:][:5]
                    price = act.get("price", 0)
                    days_text += (
                        f"    - [{act_type}] {start} {name}"
                        + (f" – {price:,} VNĐ" if price else "") + "\n"
                    )

            # Conversation history summary
            history = ""
            if state.get("conversation_summaries"):
                history = " | ".join(
                    s.get("summary", "") for s in state["conversation_summaries"][-3:]
                )

            trip_context = TRIP_CONTEXT_TEMPLATE.format(
                trip_id=trip_id,
                destination=trip.get("destination", "N/A"),
                total_budget=float(trip.get("totalBudget", 0)),
                status=trip.get("status", "N/A"),
                created_at=str(trip.get("createdAt", ""))[:19],
                day_details=days_text or "  (Chưa có lịch trình chi tiết)",
                conversation_history=history or "  (Chưa có lịch sử hội thoại)",
            )
            return {"trip_context": trip_context}
        except Exception as exc:
            logger.error(f"retrieve_trip_context_node error: {exc}")
            return {"trip_context": f"Lỗi khi tải dữ liệu chuyến đi: {exc}"}

    # Node: agent 
    def agent_node(state: AgentState) -> dict:
        logger.info("[Node] agent")
        messages = list(state["messages"])

        # Fetch recent history as context
        if state.get("short_term_memory"):
            def is_normal_text_message(msg: BaseMessage) -> bool:
                has_tool_calls = bool(getattr(msg, "tool_calls", None))
                is_tool_result = (msg.type == "tool")
                return not has_tool_calls and not is_tool_result
            clean_memory = [msg for msg in state["short_term_memory"] if is_normal_text_message(msg)]
            messages = clean_memory[-8:] + messages

        # Inject trip context as a system-style human message
        trip_context = state.get("trip_context", "")
        if trip_context:
            ctx_msg = HumanMessage(
                content=f"[CONTEXT – sử dụng thông tin này để trả lời]\n{trip_context}"
            )
            if len(messages) > 1:
                messages.insert(-1, ctx_msg)
            else:
                messages.append(ctx_msg)
        
        system_prompt = (
            f"User ID: {state['user_id']} | Trip ID: {state.get('trip_id', 'chưa chọn')}\n\n"
            f"{TRAVEL_ADVISOR_SYSTEM_PROMPT}"
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ])
        chain = prompt | llm_with_tools
        try:
            response = chain.invoke({"messages": messages})
        except Exception as exc:
            logger.error(f"agent_node LLM error: {exc}")
            error_msg = str(exc)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                user_friendly_msg = "Hệ thống đang quá tải (vượt quá giới hạn gọi API của Gemini). Vui lòng đợi khoảng 1 phút rồi thử lại nhé!"
            else:
                user_friendly_msg = f"Xin lỗi, đã có lỗi xảy ra khi xử lý yêu cầu. Lỗi hệ thống: {error_msg}"
            response = AIMessage(content=user_friendly_msg)
        return {"messages": [response]}

    # Node: direct_response 
    def direct_response_node(state: AgentState) -> dict:
        logger.info(f"[Node] direct_response: type={state.get('query_type')}")
        try:
            response = direct_response.invoke({
                "user_query": state["input"],
                "query_type": state.get("query_type", "general_chat"),
            })
            return {"messages": [AIMessage(content=response)]}
        except Exception as exc:
            logger.error(f"direct_response_node error: {exc}")
            return {"messages": [AIMessage(content="Xin chào! Tôi có thể giúp gì cho bạn? 😊")]}

    # ── Node: memory_save ─────────────────────────────────────────────────────
    def memory_save_node(state: AgentState) -> dict:
        logger.info("[Node] memory_save")
        mm = state.get("memory_manager")
        if not mm:
            return {}
        try:
            all_messages = list(state.get("short_term_memory") or []) + list(state["messages"])
            mm.save_short_term_memory(state["user_id"], all_messages)

            # Auto-summarise if conversation is long
            if len(all_messages) > 20:
                texts = [
                    m.content[:200] for m in all_messages[-12:]
                    if isinstance(m, (HumanMessage, AIMessage))
                    and isinstance(m.content, str)
                    and not m.content.startswith("[CONTEXT")
                    and len(m.content.strip()) > 15
                ]
                if len(texts) >= 3:
                    trip_id = state.get("trip_id", "")
                    dest = ""
                    if trip_id:
                        ctx = get_full_trip_context(trip_id)
                        dest = ctx.get("trip", {}).get("destination", "") if ctx else ""
                    summary = summarize_conversation.invoke({
                        "messages": texts[-8:],
                        "trip_destination": dest,
                    })
                    if summary and len(summary) > 20:
                        mm.save_conversation_summary(state["user_id"], summary)
        except Exception as exc:
            logger.error(f"memory_save_node error: {exc}")
        return {}

    # Tool node 
    tool_node = ToolNode(ALL_TOOLS)

    # Routing helpers
    def route_after_classification(state: AgentState) -> str:
        if state.get("needs_retrieval"):
            return "retrieve_trip_context"
        return "direct_response"

    def route_after_agent(state: AgentState) -> str:
        last = state["messages"][-1]
        if isinstance(last, AIMessage) and last.tool_calls:
            return "tool_node"
        return "memory_save"

    # Build graph 
    graph = StateGraph(AgentState)
    graph.add_node("memory_init", memory_init_node)
    graph.add_node("classify_query", classify_query_node)
    graph.add_node("retrieve_trip_context", retrieve_trip_context_node)
    graph.add_node("agent", agent_node)
    graph.add_node("direct_response", direct_response_node)
    graph.add_node("tool_node", tool_node)
    graph.add_node("memory_save", memory_save_node)

    graph.set_entry_point("memory_init")
    graph.add_edge("memory_init", "classify_query")
    graph.add_conditional_edges(
        "classify_query",
        route_after_classification,
        {
            "retrieve_trip_context": "retrieve_trip_context",
            "direct_response": "direct_response",
        },
    )
    graph.add_edge("retrieve_trip_context", "agent")
    graph.add_conditional_edges(
        "agent",
        route_after_agent,
        {
            "tool_node": "tool_node",
            "memory_save": "memory_save",
        },
    )
    graph.add_edge("tool_node", "agent")
    graph.add_edge("direct_response", "memory_save")
    graph.add_edge("memory_save", END)

    return graph.compile()