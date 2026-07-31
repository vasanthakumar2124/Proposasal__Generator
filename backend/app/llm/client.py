import json
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Optional

from app.config.settings import settings
from app.llm.cache import llm_cache
from app.llm.models import TASK_MODEL_MAP, MODEL_REGISTRY, TaskComplexity, ModelConfig
from app.llm.tokenizer import estimate_tokens, truncate_to_max_tokens

logger = logging.getLogger("proposalcraft.llm")


@dataclass
class LLMResponse:
    content: str
    model_used: str
    provider: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0
    latency_ms: int = 0


class LLMClient:
    def __init__(self):
        self.cache = llm_cache

    def generate(
        self,
        prompt: str,
        complexity: TaskComplexity = "medium",
        max_tokens: int = 2048,
        temperature: float = 0.3,
        use_cache: bool = True,
        model_override: Optional[str] = None,
    ) -> LLMResponse:
        if model_override:
            chain = [(model_override, "default")]
        else:
            chain = TASK_MODEL_MAP.get(complexity, TASK_MODEL_MAP["medium"])

        if use_cache:
            for provider_key, model_tier in chain:
                model_key = f"{provider_key}:{model_tier}"
                cached = self.cache.get(prompt, model_key)
                if cached:
                    return LLMResponse(content=cached, model_used=model_key, provider=provider_key)

        errors = []
        for provider_key, model_tier in chain:
            model_config = MODEL_REGISTRY.get(provider_key, {}).get(model_tier)
            if not model_config:
                continue
            try:
                return self._call_provider(model_config, prompt, max_tokens, temperature, complexity)
            except Exception as e:
                errors.append(f"{provider_key}/{model_tier}: {e}")
                logger.warning("Provider %s failed: %s", provider_key, e)
                continue

        raise RuntimeError(f"All LLM providers failed: {'; '.join(errors)}")

    def generate_json(
        self,
        prompt: str,
        complexity: TaskComplexity = "medium",
        max_tokens: int = 2048,
    ) -> dict:
        response = self.generate(prompt, complexity=complexity, max_tokens=max_tokens)
        return self._parse_json(response.content)

    def _call_provider(
        self, config: ModelConfig, prompt: str, max_tokens: int, temperature: float, complexity: str
    ) -> LLMResponse:
        start = time.time()
        input_tokens = estimate_tokens(prompt)

        prompt_limit = max(500, 5000 - max_tokens)
        truncated = truncate_to_max_tokens(prompt, prompt_limit)
        char_limit = prompt_limit * 5
        if len(truncated) > char_limit:
            truncated = truncated[:char_limit]
        actual_max = min(max_tokens, 4096)

        if config.provider == "groq":
            content = self._call_groq(config.model, truncated, actual_max, temperature)
        elif config.provider == "openai":
            content = self._call_openai(config.model, truncated, actual_max, temperature)
        elif config.provider == "ollama":
            content = self._call_ollama(config.model, truncated, actual_max, temperature)
        else:
            raise ValueError(f"Unknown provider: {config.provider}")

        latency_ms = int((time.time() - start) * 1000)
        output_tokens = estimate_tokens(content)
        cost = (input_tokens * config.cost_per_input_token) + (output_tokens * config.cost_per_output_token)

        model_key = f"{config.provider}:{config.model}"
        self.cache.set(prompt, model_key, content)

        logger.info(
            "LLM call: provider=%s model=%s input_tokens=%d output_tokens=%d cost=%.6f latency=%dms",
            config.provider, config.model, input_tokens, output_tokens, cost, latency_ms,
        )

        return LLMResponse(
            content=content,
            model_used=config.model,
            provider=config.provider,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            latency_ms=latency_ms,
        )

    def _call_groq(self, model: str, prompt: str, max_tokens: int, temperature: float) -> str:
        from groq import Groq
        client = Groq(api_key=settings.GROQ_API_KEY)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    def _call_openai(self, model: str, prompt: str, max_tokens: int, temperature: float) -> str:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    def _call_ollama(self, model: str, prompt: str, max_tokens: int, temperature: float) -> str:
        import httpx
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": max_tokens, "temperature": temperature},
        }
        resp = httpx.post(f"{settings.OLLAMA_BASE_URL}/api/generate", json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json()["response"]

    def _parse_json(self, text: str) -> dict:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
            match = re.search(r"\{[^}]+\}", text, re.DOTALL)
            if match:
                try:
                    return json.loads("{" + match.group() + "}")
                except json.JSONDecodeError:
                    pass
            return {"raw_response": text, "_parse_error": "Could not parse JSON"}


llm_client = LLMClient()
