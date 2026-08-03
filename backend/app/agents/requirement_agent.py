import json
import logging

from app.agents.base import BaseAgent
from app.llm.prompts import (
    REQUIREMENT_SYSTEM_PROMPT,
    REQUIREMENT_EXTRACTION_TEMPLATE,
    REQUIREMENT_ENRICHMENT_TEMPLATE,
)

logger = logging.getLogger("proposalcraft.agents.requirement")

# Thin-input thresholds: below these the requirements are too sparse to write
# a grounded proposal, so we infer clearly-labeled assumptions instead of
# silently proceeding with vague prose.
MIN_DESCRIPTION_WORDS = 15
MIN_CORE_FEATURES = 2


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

        result = self._enrich_thin_input(result)

        return {
            **state,
            "requirements": result,
        }

    def _enrich_thin_input(self, requirements: dict) -> dict:
        description = str(requirements.get("description", "") or "").strip()
        features = requirements.get("core_features") or []
        desc_words = len(description.split())

        if desc_words >= MIN_DESCRIPTION_WORDS and len(features) >= MIN_CORE_FEATURES:
            return requirements

        domain = requirements.get("domain", "custom")
        project_type = requirements.get("project_type", "web_app")
        try:
            enrich_prompt = REQUIREMENT_ENRICHMENT_TEMPLATE.format(
                project_type=project_type,
                domain=domain,
                description=description or "not stated",
                core_features=", ".join(str(f) for f in features) or "not stated",
            )
            enriched = self._llm_json(enrich_prompt, complexity="simple", max_tokens=800)
            assumptions = enriched.get("assumptions") if "_parse_error" not in enriched else []
            if isinstance(assumptions, list) and assumptions:
                existing = requirements.get("assumptions") or []
                requirements["assumptions"] = [*existing, *assumptions]
                requirements["additional_notes"] = (
                    "Client input was thin; assumptions above were inferred from the "
                    "stated domain and should be confirmed with the client."
                )
                logger.info(
                    "Inferred %d assumptions for thin client input (%d words, %d features)",
                    len(assumptions), desc_words, len(features),
                )
        except Exception as e:
            logger.error("Assumption enrichment failed: %s", e)

        return requirements

    def _defaults(self, state: dict, raw_hint: str = "") -> dict:
        return {
            **state,
            "requirements": {
                "project_name": state.get("project_name", "Software Project"),
                "domain": state.get("domain", "custom"),
                "project_domain_description": raw_hint or state.get("description", ""),
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
