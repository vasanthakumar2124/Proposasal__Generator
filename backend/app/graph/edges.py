from langgraph.graph import START, END

from app.graph.nodes import MAX_RUBRIC_RETRIES

NODE_ORDER = [
    "requirement",
    "business_engines",
    "rag",
    "writer",
    "reviewer",
    "finalizer",
    "rubric_check",
]


def add_edges(graph):
    graph = add_conditional_edges(graph)
    return graph


def route_after_rubric(state: dict) -> str:
    """Quality gate: send the draft back to the writer with rubric findings
    unless it passed or the retry cap is exhausted (avoid infinite loops)."""
    result = state.get("rubric_result") or {}
    passed = result.get("passed") if isinstance(result, dict) else True
    retries = state.get("rubric_retries", 0) or 0
    if passed or retries >= MAX_RUBRIC_RETRIES:
        return END
    return "writer"


def add_conditional_edges(graph):
    graph.add_edge(START, "requirement")
    graph.add_edge("requirement", "business_engines")
    graph.add_edge("business_engines", "rag")
    graph.add_edge("rag", "writer")
    graph.add_edge("writer", "reviewer")
    graph.add_edge("reviewer", "finalizer")
    graph.add_edge("finalizer", "rubric_check")
    graph.add_conditional_edges(
        "rubric_check",
        route_after_rubric,
        {"writer": "writer", END: END},
    )
    return graph
