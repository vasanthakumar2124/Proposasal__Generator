from langgraph.graph import START, END

NODE_ORDER = [
    "requirement",
    "business_engines",
    "rag",
    "writer",
    "reviewer",
    "finalizer",
]


def add_edges(graph):
    graph = add_conditional_edges(graph)
    return graph


def add_conditional_edges(graph):
    graph.add_edge(START, "requirement")
    graph.add_edge("requirement", "business_engines")
    graph.add_edge("business_engines", "rag")
    graph.add_edge("rag", "writer")
    graph.add_edge("writer", "reviewer")
    graph.add_edge("reviewer", "finalizer")
    graph.add_edge("finalizer", END)
    return graph
