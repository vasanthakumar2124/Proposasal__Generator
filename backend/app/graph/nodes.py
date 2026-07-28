from app.graph.state import ProposalState

from app.agents.requirement_agent import analyze_requirement
from app.agents.rag_agent import RAGAgent
from app.agents.feature_agent import FeatureAgent
from app.agents.business_analysis_agent import BusinessAnalysisAgent
from app.agents.proposal_writer_agent import ProposalWriterAgent
from app.agents.pdf_agent import PDFAgent


# ---------------------------------------------------------
# Requirement Node
# ---------------------------------------------------------

def requirement_node(state: ProposalState):

    state["requirement_json"] = analyze_requirement(
        state["requirement"]
    )

    return state


# ---------------------------------------------------------
# RAG Node
# ---------------------------------------------------------

def rag_node(state: ProposalState):

    rag_agent = RAGAgent()

    result = rag_agent.run(
        state["requirement_json"]
    )

    state["rag_context"] = result["retrieved_context"]

    return state


# ---------------------------------------------------------
# Feature Node
# ---------------------------------------------------------

def feature_node(state: ProposalState):

    feature_agent = FeatureAgent()

    state["features"] = feature_agent.run(
        requirement=state["requirement_json"],
        rag_context=state["rag_context"]
    )

    return state


# ---------------------------------------------------------
# Business Analysis Node
# ---------------------------------------------------------

def business_analysis_node(state: ProposalState):

    agent = BusinessAnalysisAgent()

    state["business_analysis"] = agent.run(
        requirement=state["requirement_json"],
        rag_context=state["rag_context"],
        features=state["features"]
    )

    return state


# ---------------------------------------------------------
# Proposal Writer Node
# ---------------------------------------------------------

def proposal_node(state: ProposalState):

    writer = ProposalWriterAgent()

    state["proposal"] = writer.run(
        requirement=state["requirement_json"],
        rag_context=state["rag_context"],
        features=state["features"],
        business_analysis=state["business_analysis"]
    )

    return state


# ---------------------------------------------------------
# PDF Generator Node
# ---------------------------------------------------------

def pdf_node(state: ProposalState):

    pdf_agent = PDFAgent()

    result = pdf_agent.run(
        proposal_text=state["proposal"]["proposal_content"],
        requirement=state["requirement_json"]
    )

    state["pdf_file"] = result["pdf_file"]
    state["pdf_path"] = result["pdf_file"]

    return state