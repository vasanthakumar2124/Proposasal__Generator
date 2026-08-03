import json
import logging

from app.agents.base import BaseAgent
from app.llm.prompts import REVIEWER_SYSTEM_PROMPT, PROPOSAL_REVIEWER_TEMPLATE

logger = logging.getLogger("proposalcraft.agents.reviewer")


class ReviewerAgent(BaseAgent):
    name = "reviewer_agent"

    def run(self, state: dict) -> dict:
        proposal = state.get("proposal_draft", {})
        rubric_issues = state.get("rubric_issues") or []

        if not proposal or (isinstance(proposal, dict) and "_parse_error" in proposal):
            logger.warning("No valid proposal to review, returning state unchanged")
            return {
                **state,
                "review": {
                    "review": {
                        "overall_score": 0,
                        "strengths": [],
                        "weaknesses": ["Proposal could not be generated"],
                        "clarity_score": 0,
                        "persuasiveness_score": 0,
                        "completeness_score": 0,
                        "missing_sections": ["entire proposal"],
                        "suggestions": ["Retry generation with more complete data"],
                    },
                    "improved_proposal": {},
                },
            }

        try:
            rubric_section = (
                "\n".join(f"- {i}" for i in rubric_issues)
                if rubric_issues
                else "None"
            )
            prompt = f"{REVIEWER_SYSTEM_PROMPT}\n\n{PROPOSAL_REVIEWER_TEMPLATE.format(
                proposal_json=json.dumps(proposal, indent=2),
                rubric_issues_section=rubric_section,
            )}"

            result = self._llm_json(prompt, complexity="medium", max_tokens=8192)
        except Exception as e:
            logger.error("Reviewer agent LLM call failed: %s", e)
            result = {"_parse_error": str(e)}

        if "_parse_error" in result:
            logger.error("Reviewer agent JSON parse error")
            return {
                **state,
                "review": {
                    "review": {
                        "overall_score": 5,
                        "strengths": [],
                        "weaknesses": ["Could not complete review"],
                        "clarity_score": 5,
                        "persuasiveness_score": 5,
                        "completeness_score": 5,
                        "missing_sections": [],
                        "suggestions": ["Manual review recommended"],
                    },
                    "improved_proposal": proposal,
                },
            }

        return {
            **state,
            "review": result,
        }
