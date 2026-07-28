from langgraph.graph import END


def add_edges(graph):

    graph.set_entry_point("requirement")

    graph.add_edge(
        "requirement",
        "rag"
    )

    graph.add_edge(
        "rag",
        "feature"
    )

    graph.add_edge(
        "feature",
        "business_analysis"
    )

    graph.add_edge(
        "business_analysis",
        "proposal"
    )

    graph.add_edge(
        "proposal",
        "pdf"
    )

    graph.add_edge(
        "pdf",
        END
    )

    return graph