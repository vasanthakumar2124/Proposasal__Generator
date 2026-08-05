import json

from app.agents.writer_agent import WriterAgent
from app.llm.prompts import WRITER_BATCHES


class FakeLLM:
    def __init__(self):
        self.calls = []

    def generate_json(self, prompt, complexity="simple", max_tokens=2048):
        self.calls.append(prompt)
        if '"executive_summary": {' in prompt:
            return {
                "executive_summary": {"business_overview": "one"},
                "client_understanding": {"business_overview": "two"},
                "requirement_analysis": {"functional_requirements": ["three"]},
            }
        if '"proposed_solution": {' in prompt:
            return {
                "proposed_solution": {"overview": "four"},
                "security": {"authentication": "five"},
                "terms": {"confidentiality": "six"},
            }
        return {"conclusion": {"summary": "seven"}}


class TestWriterAgentBatching:
    def setup_method(self):
        self.llm = FakeLLM()
        self.agent = WriterAgent(self.llm)

    def _state(self, **overrides):
        state = {
            "requirements": {
                "domain": "custom",
                "project_type": "web_app",
                "description": "A car marketplace with listings, search, and messaging.",
                "core_features": ["listings", "search"],
            },
            "business_context": {
                "module_data": {"modules": [{"name": "Listings"}]},
                "tech_stack_data": {"technology_stack": {"frontend": [{"name": "React 19"}]}},
                "pricing_data": {"one_time_cost": 50000},
                "timeline_data": {"phases": [{"name": "Discovery", "duration_weeks": 2}]},
                "diagram_data": {"workflow_svg": "HUGESVG" * 1000},
            },
            "rubric_issues": [],
            "rubric_retries": 0,
        }
        state.update(overrides)
        return state

    def test_all_batches_merged_into_single_draft(self):
        result = self.agent.run(self._state())
        draft = result["proposal_draft"]
        assert set(draft.keys()) == {
            "executive_summary",
            "client_understanding",
            "requirement_analysis",
            "proposed_solution",
            "security",
            "terms",
            "conclusion",
        }
        assert draft["conclusion"]["summary"] == "seven"

    def test_three_llm_calls_issued(self):
        self.agent.run(self._state())
        assert len(self.llm.calls) == len(WRITER_BATCHES)

    def test_context_filtered_to_grounding_keys(self):
        self.agent.run(self._state())
        # diagram SVGs must never reach the writer prompt (token waste)
        assert "HUGESVG" not in self.llm.calls[0]
        assert "React 19" in self.llm.calls[0] or "module_data" in self.llm.calls[0]

    def test_rubric_issues_injected_on_retry(self):
        issues = ["executive_summary: 30 words (min 120)", "Missing sections: ['security']"]
        result = self.agent.run(self._state(rubric_issues=issues, rubric_retries=1))
        assert result["proposal_draft"]
        last_prompt = self.llm.calls[-1]
        assert "fix them specifically" in last_prompt
        assert "executive_summary: 30 words" in last_prompt

    def test_no_issues_no_rubric_section(self):
        self.agent.run(self._state())
        assert "fix them specifically" not in self.llm.calls[0]

    def test_parse_failure_does_not_kill_other_batches(self):
        class PartialLLM(FakeLLM):
            def generate_json(self, prompt, complexity="simple", max_tokens=2048):
                self.calls.append(prompt)
                if '"executive_summary": {' in prompt:
                    return {"raw_response": "not json", "_parse_error": "boom"}
                return super().generate_json(prompt)

        agent = WriterAgent(PartialLLM())
        result = agent.run(self._state())
        draft = result["proposal_draft"]
        assert "executive_summary" not in draft
        assert "proposed_solution" in draft
        assert "conclusion" in draft

    def test_parse_failure_retried_once_with_strict_instruction(self):
        class FlakyLLM(FakeLLM):
            def __init__(self):
                super().__init__()
                self.fail_once = True

            def generate_json(self, prompt, complexity="simple", max_tokens=2048):
                self.calls.append(prompt)
                if self.fail_once and '"executive_summary": {' in prompt:
                    self.fail_once = False
                    return {"raw_response": "not json", "_parse_error": "boom"}
                return super().generate_json(prompt)

        llm = FlakyLLM()
        agent = WriterAgent(llm)
        result = agent.run(self._state())
        draft = result["proposal_draft"]
        assert "executive_summary" in draft
        assert any("CRITICAL: The previous output was not valid JSON" in p for p in llm.calls)
