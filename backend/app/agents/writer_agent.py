import json
import logging

from app.agents.base import BaseAgent
from app.llm.prompts import WRITER_SYSTEM_PROMPT, PROPOSAL_WRITER_TEMPLATE
from app.llm.tokenizer import estimate_tokens, truncate_to_max_tokens

logger = logging.getLogger("proposalcraft.agents.writer")

# Groq free tier TPM limit is 6000 for fast model. Keep prompt+max_tokens under 6000.
MAX_PROMPT_TOKENS = 3500


class WriterAgent(BaseAgent):
    name = "writer_agent"

    def run(self, state: dict) -> dict:
        requirements = state.get("requirements", {})
        business_context = state.get("business_context", {})
        rag_context = state.get("rag_context", {})

        for key in business_context.get("reporting", {}):
            if isinstance(business_context["reporting"][key], (dict, list)):
                business_context["reporting"][key] = json.dumps(business_context["reporting"][key])

        try:
            req_json = json.dumps(requirements, indent=2)
            ctx_json = json.dumps(business_context, indent=2)

            template_prefix = f"{WRITER_SYSTEM_PROMPT}\n\n{PROPOSAL_WRITER_TEMPLATE}"
            prefix_tokens = estimate_tokens(template_prefix)
            data_budget = MAX_PROMPT_TOKENS - prefix_tokens

            if data_budget > 0:
                req_tokens = estimate_tokens(req_json)
                ctx_tokens = estimate_tokens(ctx_json)
                total_data = req_tokens + ctx_tokens

                if total_data > data_budget:
                    if ctx_tokens > req_tokens:
                        ctx_json = truncate_to_max_tokens(ctx_json, data_budget - req_tokens)
                    else:
                        req_json = truncate_to_max_tokens(req_json, data_budget - ctx_tokens)

            prompt = f"{template_prefix.format(requirements_json=req_json, business_context_json=ctx_json)}"
            result = self._llm_json(prompt, complexity="simple", max_tokens=4096)
        except Exception as e:
            logger.error("Writer agent LLM call failed: %s", e, exc_info=True)
            raise

        if "_parse_error" in result:
            logger.error("Writer agent JSON parse error, returning raw text")
            return {
                **state,
                "proposal_draft": result,
                "proposal_text": result.get("raw_response", ""),
            }

        return {
            **state,
            "proposal_draft": result,
        }
