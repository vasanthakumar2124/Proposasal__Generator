from langgraph.graph import StateGraph

from app.graph.state import ProposalState
from app.graph.nodes import (
    requirement_node,
    business_engines_node,
    rag_node,
    writer_node,
    reviewer_node,
    rubric_node,
    finalizer_node,
)
from app.graph.edges import add_edges


def build_workflow():
    graph = StateGraph(ProposalState)

    graph.add_node("requirement", requirement_node)
    graph.add_node("business_engines", business_engines_node)
    graph.add_node("rag", rag_node)
    graph.add_node("writer", writer_node)
    graph.add_node("reviewer", reviewer_node)
    graph.add_node("finalizer", finalizer_node)
    graph.add_node("rubric_check", rubric_node)

    graph = add_edges(graph)

    workflow = graph.compile()

    return workflow


proposal_workflow = build_workflow()
