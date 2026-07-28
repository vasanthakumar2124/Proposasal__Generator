from langgraph.graph import StateGraph

from app.graph.state import ProposalState

from app.graph.nodes import (
    requirement_node,
    rag_node,
    feature_node,
    business_analysis_node,
    proposal_node,
    pdf_node,
)

from app.graph.edges import add_edges


def build_workflow():

    graph = StateGraph(ProposalState)

    # ------------------------------------
    # Register Nodes
    # ------------------------------------

    graph.add_node(
        "requirement",
        requirement_node
    )

    graph.add_node(
        "rag",
        rag_node
    )

    graph.add_node(
        "feature",
        feature_node
    )

    graph.add_node(
        "business_analysis",
        business_analysis_node
    )

    graph.add_node(
        "proposal",
        proposal_node
    )

    graph.add_node(
        "pdf",
        pdf_node
    )

    # ------------------------------------
    # Connect Nodes
    # ------------------------------------

    graph = add_edges(graph)

    # ------------------------------------
    # Compile Graph
    # ------------------------------------

    workflow = graph.compile()

    return workflow