import logging

from app.agents.base import BaseAgent
from app.llm.prompts import RAG_SYSTEM_PROMPT, RAG_CONTEXT_TEMPLATE
from app.llm.tokenizer import estimate_tokens, truncate_to_max_tokens

logger = logging.getLogger("proposalcraft.agents.rag")

# groq/fast (llama-3.1-8b-instant) has TPM limit ~6000
MAX_PROMPT_TOKENS = 4000


class RAGAgent(BaseAgent):
    name = "rag_agent"

    def run(self, state: dict) -> dict:
        rag_chunks = state.get("rag_chunks", [])
        domain = state.get("requirements", {}).get("domain", "custom")
        description = state.get("requirements", {}).get("description", "")

        if not rag_chunks:
            logger.info("No RAG chunks provided, returning default context")
            return {
                **state,
                "rag_context": {
                    "domain_insights": [],
                    "technical_insights": [],
                    "best_practices": [],
                    "relevant_case_studies": [],
                    "key_considerations": [],
                },
            }

        raw_chunks = "\n---\n".join(
            [c if isinstance(c, str) else c.get("content", str(c)) for c in rag_chunks]
        )

        template_prefix = f"{RAG_SYSTEM_PROMPT}\n\n{RAG_CONTEXT_TEMPLATE}"
        prefix_tokens = estimate_tokens(template_prefix)
        data_budget = MAX_PROMPT_TOKENS - prefix_tokens
        truncated_chunks = truncate_to_max_tokens(raw_chunks, data_budget) if data_budget > 0 else ""

        try:
            prompt = f"{RAG_SYSTEM_PROMPT}\n\n{RAG_CONTEXT_TEMPLATE.format(
                domain=domain,
                description=description,
                rag_chunks=truncated_chunks,
            )}"
            result = self._llm_json(prompt, complexity="simple")
        except Exception as e:
            logger.error("RAG agent LLM call failed: %s", e)
            result = {
                "domain_insights": [],
                "technical_insights": [],
                "best_practices": [],
                "relevant_case_studies": [],
                "key_considerations": [],
            }

        return {
            **state,
            "rag_context": result,
        }
