"""
workflow/nodes/Mobility_agent.py

Mobility Node — Logic-First, AI-Refined (two-layer architecture).

Stage 1 — Hard Constraints (Pure Python, no LLM):
  Neo4j   → fetch Ward-to-Ward routes (distance_km)
  MongoDB → fetch real transport providers by ward
  Python  → classify type | estimate price | filter budget/health | rank by suitability
  Result  → Feasible Candidates (guaranteed correct numbers)

Stage 2 — Soft Constraints (AI Refinement, ranking only):
  LLM     → re-rank feasible candidates based on 'vibe' / emotional preferences
  Fallback→ if LLM fails, original logic ranking is preserved
  Result  → Human-friendly ordered transportation list
"""

from __future__ import annotations

import json
import os
from typing import List, Optional
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from workflow.db import get_mongo_db, get_neo4j_driver
from workflow.graph.stage import State

load_dotenv()

# ==========================================
# TRANSPORT CLASSIFICATION TABLE
# Rules are evaluated in order (first match wins).
# ==========================================

_TRANSPORT_RULES: list[dict] = [
    {
        "max_km": 1.0,
        "type": "walking",
        "base_price": 0,
        "price_per_km": 0,
        "suitability": ["Solo", "Couples"],
    },
    {
        "max_km": 3.0,
        "type": "bicycle",
        "base_price": 10_000,
        "price_per_km": 3_000,
        "suitability": ["Solo", "Couples", "Friends"],
    },
    {
        "max_km": 8.0,
        "type": "motorbike",
        "base_price": 15_000,
        "price_per_km": 3_500,
        "suitability": ["Solo", "Couples", "Friends"],
    },
    {
        "max_km": 20.0,
        "type": "taxi",
        "base_price": 25_000,
        "price_per_km": 8_000,
        "suitability": ["Solo", "Couples", "Family", "Friends"],
    },
    {
        "max_km": 60.0,
        "type": "bus",
        "base_price": 30_000,
        "price_per_km": 1_500,
        "suitability": ["Solo", "Friends", "Group"],
    },
    {
        "max_km": 300.0,
        "type": "coach",
        "base_price": 80_000,
        "price_per_km": 1_200,
        "suitability": ["Family", "Group", "Friends", "Couples"],
    },
    {
        "max_km": float("inf"),
        "type": "train",
        "base_price": 200_000,
        "price_per_km": 800,
        "suitability": ["Solo", "Couples", "Family", "Friends", "Group"],
    },
]

# ==========================================
# PURE-PYTHON LOGIC HELPERS
# ==========================================

def _classify(distance_km: float) -> dict:
    """Return the first rule whose max_km >= distance_km."""
    for rule in _TRANSPORT_RULES:
        if distance_km <= rule["max_km"]:
            return rule
    return _TRANSPORT_RULES[-1]


def _estimate_price(distance_km: float, rule: dict) -> int:
    """Linear pricing formula: base + rate × distance (rounded to nearest 1 000 VNĐ)."""
    raw = rule["base_price"] + rule["price_per_km"] * distance_km
    return int(round(raw / 1_000) * 1_000)


def _within_budget(price_per_person: int, group_size: int, budget: int) -> bool:
    """Total transport spend must not exceed the travel budget."""
    return price_per_person * group_size <= budget


def _suitability_score(rule: dict, companion_types: list[str]) -> int:
    """Count how many requested companion types the transport supports."""
    return len(set(rule["suitability"]) & set(companion_types))


def _build_note(candidate: dict, group_size: int, travel_preferences: dict) -> str:
    """Generate a Vietnamese note string from computed fields — no LLM needed."""
    t = candidate["type"]
    dist = candidate["distance_km"]
    price = candidate["price_per_person"]
    total = price * group_size
    parts: list[str] = []

    if dist == 0:
        parts.append("Điểm đến nằm trong khu vực, có thể đi bộ.")
    else:
        parts.append(f"Quãng đường {dist:.1f} km.")

    parts.append(
        f"Chi phí ước tính: {price:,.0f} VNĐ/người"
        + (f" × {group_size} người = {total:,.0f} VNĐ." if group_size > 1 else ".")
    )

    pace = travel_preferences.get("travel_pace", [])
    if any("thong" in p.lower() for p in pace):
        parts.append("Phù hợp với nhịp du lịch thong thả.")
    elif any("kham" in p.lower() or "nhanh" in p.lower() for p in pace):
        parts.append("Lý tưởng cho lịch trình dày đặc.")

    type_notes = {
        "walking":  "Không tốn chi phí, tốt cho sức khỏe.",
        "bicycle":  "Thân thiện môi trường, linh hoạt.",
        "motorbike":"Cơ động, dễ tìm thuê tại địa phương.",
        "taxi":     "Thoải mái, đặt qua app Grab hoặc gọi trực tiếp.",
        "bus":      "Tiết kiệm chi phí, phù hợp nhóm đông.",
        "coach":    "Xe giường nằm/ngồi, phù hợp chặng dài.",
        "train":    "An toàn, đúng giờ — nên đặt vé trước.",
    }
    if t in type_notes:
        parts.append(type_notes[t])

    return " ".join(parts)


# ==========================================
# DATABASE FETCH FUNCTIONS
# ==========================================

_TRANSPORT_CATS = ["Transport", "Transportation", "Mobility"]

_PROJECTION = {
    "_id": 0,
    "locationId": 1,
    "name": 1,
    "category": 1,
    "estimatedPrice": 1,
    "suitabilityFor": 1,
    "ward_name": 1,
}


def fetch_connected_wards(destination: str) -> tuple[list[str], list[dict]]:
    """
    Neo4j:
      - All Ward names under the Province  (for MongoDB filter)
      - All CONNECTED_TO edges             (from_ward, to_ward, distance_km)
    """
    driver = get_neo4j_driver()
    with driver.session() as session:
        ward_rows = session.run(
            "MATCH (p:Province {name: $dest})-[:HAS]->(w:Ward) "
            "RETURN w.name AS ward_name",
            dest=destination,
        ).data()
        route_rows = session.run(
            "MATCH (p:Province {name: $dest})-[:HAS]->(w1:Ward) "
            "MATCH (w1)-[r:CONNECTED_TO]->(w2:Ward) "
            "RETURN w1.name AS from_ward, w2.name AS to_ward, "
            "r.distance_km AS distance_km",
            dest=destination,
        ).data()

    ward_names = [r["ward_name"] for r in ward_rows]
    routes = [
        {
            "from_ward": r["from_ward"],
            "to_ward": r["to_ward"],
            "distance_km": float(r["distance_km"] or 0),
        }
        for r in route_rows
    ]
    return ward_names, routes


def fetch_transport_options(ward_names: list[str]) -> list[dict]:
    """MongoDB: Transport providers from Transportations collection."""
    if not ward_names:
        return []
    db = get_mongo_db("TravelDB")
    return list(
        db["Transportations"].find(
            {},
            {
                "_id": 0,
                "transportId": 1,
                "transportType": 1,
                "name": 1,
                "price": 1,
            },
        )
    )


# ==========================================
# CORE PYTHON LOGIC LAYER
# ==========================================

def build_transport_candidates(
    routes: list[dict],
    providers: list[dict],
    constraints: dict,
    travel_preferences: dict,
) -> list[dict]:
    """
    ALL numeric decisions happen here — no LLM involved.

    For each Neo4j route:
      1. Classify transport type by distance_km (rule table)
      2. Estimate price_per_person (linear formula)
      3. Hard-filter by budget  (price × group_size <= travel_budget)
      4. Hard-filter by mobility_limitations
      5. Score suitability by companion_type match
      6. Attach real MongoDB provider name/id if available
      7. Generate note string from templates

    Returns a ranked list ready to be stored in state.
    """
    group_size = max(int(constraints.get("group_size") or 1), 1)
    raw_budget = constraints.get("travel_budget")
    budget     = int(raw_budget) if raw_budget is not None else 10_000_000
    companion_types      = travel_preferences.get("companion_type", [])
    mobility_limitations = [
        l.lower() for l in (constraints.get("mobility_limitations") or [])
    ]

    # Provider lookup: ward_name → first provider found
    provider_by_ward: dict[str, dict] = {}
    for p in providers:
        w = p.get("ward_name", "")
        if w and w not in provider_by_ward:
            provider_by_ward[w] = p

    candidates: list[dict] = []
    seen_pairs: set[tuple] = set()

    for route in routes:
        from_w = route["from_ward"]
        to_w   = route["to_ward"]
        dist   = route["distance_km"]

        # De-duplicate identical routes
        if (from_w, to_w) in seen_pairs:
            continue
        seen_pairs.add((from_w, to_w))

        # ── Step 1: classify ──────────────────────────────────────────────────
        rule = _classify(dist)
        t    = rule["type"]

        # ── Step 2: hard-filter mobility limitations ──────────────────────────
        if any(lim in t for lim in mobility_limitations):
            continue

        # ── Step 3: estimate price ────────────────────────────────────────────
        price = _estimate_price(dist, rule)

        # ── Step 4: hard-filter budget ────────────────────────────────────────
        if not _within_budget(price, group_size, budget):
            continue

        # ── Step 5: suitability score ─────────────────────────────────────────
        score = _suitability_score(rule, companion_types)

        # ── Step 6: attach real provider ─────────────────────────────────────
        provider = provider_by_ward.get(from_w) or provider_by_ward.get(to_w)

        candidate = {
            "locationId":       provider.get("locationId") if provider else None,
            "name":             provider["name"] if provider else f"{t.title()} ({from_w} → {to_w})",
            "type":             t,
            "from_ward":        from_w,
            "to_ward":          to_w,
            "distance_km":      dist,
            "price_per_person": price,
            "suitability_for":  rule["suitability"],
            "_score":           score,
        }

        # ── Step 7: template note ─────────────────────────────────────────────
        candidate["note"] = _build_note(candidate, group_size, travel_preferences)

        candidates.append(candidate)

    # ── Rank: suitability score desc, then price asc ─────────────────────────
    candidates.sort(key=lambda c: (-c["_score"], c["price_per_person"]))

    # Clean internal field
    for c in candidates:
        c.pop("_score", None)

    return candidates


# ==========================================
# STAGE 2 — AI REFINEMENT LAYER
# ==========================================

class RankedOrder(BaseModel):
    """Structured LLM output: a re-ordered list of candidate IDs."""
    ranked_ids: List[int] = Field(
        description="Danh sách ID của các phương án di chuyển, đã được sắp xếp lại theo "
                    "thứ tự ưu tiên từ phù hợp nhất đến ít phù hợp nhất."
    )


_refine_prompt = ChatPromptTemplate.from_messages([
    ("system", """
Bạn là chuyên gia tư vấn trải nghiệm du lịch.
Nhiệm vụ DUY NHẤT của bạn là XẾP HẠNG LẠI danh sách phương tiện di chuyển dưới đây
dựa trên cảm xúc, phong cách và "vibe" mà người dùng mong muốn.

QUY TẮC BẮT BUỘC:
- TUYỆT ĐỐI KHÔNG thay đổi giá, khoảng cách hay bất kỳ con số nào — các giá trị đó đã được xác minh.
- TUYỆT ĐỐI KHÔNG loại bỏ hay thêm phương án nào — chỉ sắp xếp lại.
- Chỉ trả về danh sách ID theo thứ tự ưu tiên mới.

GỢI Ý XẾP HẠNG theo phong cách:
- "Chill", "Thong thả", "Lãng mạn" → Ưu tiên: walking > bicycle > motorbike
- "Khám phá", "Năng động"           → Ưu tiên: motorbike > bicycle > taxi
- "Sang trọng", "Tiện nghi"         → Ưu tiên: taxi > coach > train
- "Tiết kiệm", "Bụi"               → Ưu tiên: bus > bicycle > walking
- Nhóm gia đình / trẻ em            → Ưu tiên: taxi > coach > bus
"""),
    ("human", """
Sở thích và phong cách du lịch của người dùng:
{preferences}

Danh sách phương án khả thi (đã qua bộ lọc ngân sách & sức khỏe):
{candidates}

Hãy trả về danh sách ID theo thứ tự ưu tiên mới.
""")
])

_refine_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.5,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)
_refine_chain = _refine_prompt | _refine_llm.with_structured_output(RankedOrder)


def refine_with_ai(
    candidates: list[dict],
    travel_preferences: dict,
) -> list[dict]:
    """
    Stage 2 — AI Refinement Layer (Soft Constraints).

    Sends a token-efficient summary of feasible candidates to the LLM.
    The LLM re-ranks by 'vibe' / emotional fit — it CANNOT change any numbers.
    Falls back to the original logic-ranked order on any LLM error.

    Args:
        candidates: Output of build_transport_candidates() — already budget-safe.
        travel_preferences: User's style preferences from state.

    Returns:
        The same candidates list, re-ordered by the LLM's ranking.
    """
    if not candidates:
        return []

    # ── Token-efficient summary: only semantics, no numbers ───────────────────
    summary = [
        {
            "id":   i,
            "type": c["type"],
            "name": c["name"],
            "note": c["note"],
        }
        for i, c in enumerate(candidates)
    ]

    # ── Relevant preference fields for ranking ────────────────────────────────
    pref_summary = {
        "travel_style":    travel_preferences.get("travel_style", []),
        "travel_pace":     travel_preferences.get("travel_pace", []),
        "atmosphere":      travel_preferences.get("atmosphere", []),
        "companion_type":  travel_preferences.get("companion_type", []),
        "mobility_style":  travel_preferences.get("mobility_style", []),
    }

    try:
        response: RankedOrder = _refine_chain.invoke({
            "preferences": json.dumps(pref_summary, ensure_ascii=False),
            "candidates":  json.dumps(summary,      ensure_ascii=False),
        })

        # ── Validate returned IDs ─────────────────────────────────────────────
        valid_ids   = set(range(len(candidates)))
        returned    = response.ranked_ids
        returned_set = set(returned)

        # If LLM returned an incomplete or invalid set, fall back
        if returned_set != valid_ids:
            return candidates

        return [candidates[i] for i in returned]

    except Exception:
        # Graceful fallback: original logic order is always safe
        return candidates


# ==========================================
# LANGGRAPH NODE FUNCTION
# ==========================================

def mobility_node(state: State) -> State:
    """
    Mobility node — Logic-First, AI-Refined.

    Stage 1 (Pure Python):
      Neo4j → MongoDB → classify / price / filter / rank
      Guarantees all numbers are correct and constraints are satisfied.

    Stage 2 (AI Refinement):
      LLM re-ranks the feasible list based on emotional/style fit.
      Falls back to logic order if LLM fails.
    """
    trip_metadata      = state.get("trip_metadata", {})
    travel_preferences = state.get("travel_preferences", {})
    constraints        = state.get("constraints", {})

    destination = trip_metadata.get("destination", "")
    if isinstance(destination, list):
        destination = destination[0] if destination else ""

    # ── Stage 1: Hard Constraints (Pure Python) ───────────────────────────────
    ward_names, routes = fetch_connected_wards(destination)
    providers          = fetch_transport_options(ward_names)
    feasible           = build_transport_candidates(
        routes, providers, constraints, travel_preferences
    )

    # ── Stage 2: Soft Constraints (AI Refinement) ─────────────────────────────
    transportations = refine_with_ai(feasible, travel_preferences)

    # Update state with transportations
    state["transportations"] = transportations
    
    return state