import json
import logging

from app.agents.base import BaseAgent
from app.llm.prompts import WRITER_SYSTEM_PROMPT, WRITER_BATCHES, build_writer_template
from app.llm.tokenizer import estimate_tokens, truncate_to_max_tokens

logger = logging.getLogger("proposalcraft.agents.writer")

# Groq free tier TPM limit means total tokens per minute are capped. The writer
# now runs in 2-3 batched calls, so this cap is per-batch input, and the
# business context is pre-filtered to only the fields relevant for grounding
# (module/stack/pricing/timeline/team/roi/risk numbers) instead of truncating
# indiscriminately.
MAX_PROMPT_TOKENS = 3500

# Keys of business_context the writer actually needs for grounding. Everything
# else (diagram SVGs, template config, raw engine internals) is dropped to keep
# each batch's prompt small and focused.
WRITER_CONTEXT_ALLOWLIST = {
    "industry_data",
    "module_data",
    "feature_data",
    "automation_data",
    "integration_data",
    "tech_stack_data",
    "timeline_data",
    "pricing_data",
    "team_data",
    "roi_data",
    "risk_data",
    "commercial_data",
    "support_data",
    "sla_data",
    "proposal_summary",
}


def _filter_business_context(business_context: dict) -> dict:
    return {k: v for k, v in business_context.items() if k in WRITER_CONTEXT_ALLOWLIST}


def _format_rubric_issues(rubric_issues: list) -> str:
    if not rubric_issues:
        return ""
    issues = "\n".join(f"- {i}" for i in rubric_issues)
    return (
        "The following issues were found in the previous draft — fix them specifically:\n"
        f"{issues}"
    )


class WriterAgent(BaseAgent):
    name = "writer_agent"

    def run(self, state: dict) -> dict:
        requirements = state.get("requirements", {}) or {}
        business_context = _filter_business_context(state.get("business_context", {}) or {})
        rubric_issues = state.get("rubric_issues") or []
        retry_count = state.get("rubric_retries", 0) or 0

        if retry_count:
            logger.info("Writer retry #%d with rubric findings: %s", retry_count, rubric_issues)

        try:
            req_json = json.dumps(requirements, indent=2)
            ctx_json = json.dumps(business_context, indent=2)
        except (TypeError, ValueError) as e:
            logger.error("Writer could not serialize context: %s", e)
            return {
                **state,
                "proposal_draft": {
                    "_parse_error": "Could not serialize context",
                    "raw_response": str(e),
                },
            }

        draft = {}
        errors = []
        for batch_keys in WRITER_BATCHES:
            result = self._run_batch(
                batch_keys,
                requirements,
                req_json,
                ctx_json,
                rubric_issues,
            )
            if "_parse_error" in result:
                errors.append(f"{','.join(batch_keys)}: {result['_parse_error']}")
                logger.error("Writer batch %s failed: %s", batch_keys, result["_parse_error"])
                continue
            draft.update(result)

        if not draft and errors:
            return {
                **state,
                "proposal_draft": {
                    "_parse_error": "; ".join(errors),
                    "raw_response": "",
                },
            }

        return {
            **state,
            "proposal_draft": draft,
        }

    def _run_batch(
        self,
        batch_keys: tuple[str, ...],
        requirements: dict,
        req_json: str,
        ctx_json: str,
        rubric_issues: list,
    ) -> dict:
        template_prefix = f"{WRITER_SYSTEM_PROMPT}\n\n{build_writer_template(batch_keys)}"
        prefix_tokens = estimate_tokens(template_prefix)
        data_budget = MAX_PROMPT_TOKENS - prefix_tokens

        batch_req_json = req_json
        batch_ctx_json = ctx_json
        if data_budget > 0:
            req_tokens = estimate_tokens(batch_req_json)
            ctx_tokens = estimate_tokens(batch_ctx_json)
            total_data = req_tokens + ctx_tokens
            if total_data > data_budget:
                # Requirements stay intact as long as possible; the business
                # context is redundant context, so it is truncated first.
                if ctx_tokens > req_tokens:
                    batch_ctx_json = truncate_to_max_tokens(batch_ctx_json, data_budget - req_tokens)
                else:
                    batch_req_json = truncate_to_max_tokens(batch_req_json, data_budget - ctx_tokens)

        rubric_section = _format_rubric_issues(rubric_issues)

        prompt = template_prefix.format(
            requirements_json=batch_req_json,
            business_context_json=batch_ctx_json,
            rubric_issues_section=rubric_section,
        )

        # complexity=medium: chain is gpt-4o-mini -> llama-3.3-70b -> llama-3.1-8b,
        # so the proposal-writing call lands on a mid-tier+ model, not the 8B
        # instant model that "simple" would pick first.
        return self._llm_json(prompt, complexity="medium", max_tokens=4096)
