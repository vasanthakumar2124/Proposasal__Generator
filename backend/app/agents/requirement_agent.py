import json
import logging

from app.agents.base import BaseAgent
from app.llm.prompts import REQUIREMENT_SYSTEM_PROMPT, REQUIREMENT_EXTRACTION_TEMPLATE

logger = logging.getLogger("proposalcraft.agents.requirement")


class RequirementAgent(BaseAgent):
    name = "requirement_agent"

    def run(self, state: dict) -> dict:
        client_input = state.get("raw_client_input", "")
        if not client_input:
            logger.warning("No client input provided, using defaults")
            return self._defaults(state)

        prompt = f"{REQUIREMENT_SYSTEM_PROMPT}\n\n{REQUIREMENT_EXTRACTION_TEMPLATE.format(client_input=client_input)}"
        try:
            result = self._llm_json(prompt, complexity="medium")
        except Exception as e:
            logger.error("LLM call failed, using defaults: %s", e)
            return self._defaults(state, client_input)

        if "_parse_error" in result:
            logger.error("Failed to parse requirements: %s", result["_parse_error"])
            return self._defaults(state, result.get("raw_response", ""))

        return {
            **state,
            "requirements": result,
        }

    def _defaults(self, state: dict, raw_hint: str = "") -> dict:
        return {
            **state,
            "requirements": {
                "project_name": state.get("project_name", "Software Project"),
                "domain": state.get("domain", "custom"),
                "project_type": state.get("project_type", "web_app"),
                "description": raw_hint or state.get("description", "Custom software development project"),
                "core_features": state.get("features", []),
                "target_audience": state.get("target_audience", "End users"),
                "timeline_constraint": state.get("timeline", "normal"),
                "budget_range": state.get("budget", "mid"),
                "technical_context": "",
                "additional_notes": "",
            },
        }
