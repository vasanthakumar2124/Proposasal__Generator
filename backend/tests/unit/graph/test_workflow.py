import pytest
from app.graph.workflow import build_workflow


class TestProposalWorkflow:
    def test_workflow_builds(self):
        workflow = build_workflow()
        assert workflow is not None

    def test_workflow_has_correct_nodes(self):
        workflow = build_workflow()
        expected = {"requirement", "business_engines", "rag", "writer", "reviewer", "finalizer", "rubric_check"}
        actual = set(workflow.nodes.keys()) - {"__start__"}
        assert actual == expected, f"Expected {expected}, got {actual}"

    def test_workflow_node_order(self):
        workflow = build_workflow()
        nodes = [n for n in workflow.nodes.keys() if n != "__start__"]
        expected = ["requirement", "business_engines", "rag", "writer", "reviewer", "finalizer", "rubric_check"]
        assert nodes == expected
