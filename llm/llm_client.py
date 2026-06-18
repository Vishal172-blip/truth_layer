from __future__ import annotations

import json
import logging
import time
from typing import Literal

from openai import OpenAI

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import get_logger
from config import (
    GROQ_API_KEY,
    GROQ_BASE_URL,
    GROQ_FAST_MODEL,
    GROQ_REASONING_MODEL,
    LLM_TIMEOUT_SECONDS,
    MAX_RETRIES_ON_FAILURE,
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_FALLBACK_MODEL,
    PREFER_OPENROUTER,
)

logger = get_logger(__name__)


class LLMProviderError(Exception):
    """Raised when both Groq and OpenRouter fail to return a response."""


class LLMParseError(Exception):
    """Raised when JSON parsing fails after retries. Includes the raw response in the message."""


class LLMClient:
    def __init__(self) -> None:
        groq_client: OpenAI | None = (
            OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL, timeout=LLM_TIMEOUT_SECONDS)
            if GROQ_API_KEY is not None
            else None
        )
        openrouter_client: OpenAI | None = (
            OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_BASE_URL, timeout=LLM_TIMEOUT_SECONDS)
            if OPENROUTER_API_KEY is not None
            else None
        )

        # When both keys are present, PREFER_OPENROUTER decides which is primary.
        # While Groq's daily token quota is exhausted, making OpenRouter primary
        # avoids wasting MAX_RETRIES_ON_FAILURE retries on Groq's guaranteed 429s.
        prefer_openrouter = PREFER_OPENROUTER and openrouter_client is not None

        if groq_client is not None and not prefer_openrouter:
            self.primary: OpenAI | None = groq_client
            self.primary_name: str = "Groq"
            self.fallback: OpenAI | None = openrouter_client
            self.fallback_name: str = "OpenRouter" if openrouter_client is not None else ""
            self._primary_is_groq: bool = True
        elif openrouter_client is not None:
            self.primary = openrouter_client
            self.primary_name = "OpenRouter"
            self.fallback = groq_client
            self.fallback_name = "Groq" if groq_client is not None else ""
            self._primary_is_groq = False
        else:
            self.primary = None
            self.primary_name = "OpenRouter"
            self.fallback = None
            self.fallback_name = ""
            self._primary_is_groq = False

    def _model_for_client(self, is_groq: bool, tier: Literal["fast", "reasoning"]) -> str:
        if is_groq:
            return GROQ_FAST_MODEL if tier == "fast" else GROQ_REASONING_MODEL
        return OPENROUTER_FALLBACK_MODEL

    def _call_client(
        self,
        client: OpenAI,
        model: str,
        system: str,
        user: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content = response.choices[0].message.content
        if content is None:
            raise LLMProviderError("Provider returned an empty message content.")
        return content

    def chat(
        self,
        system: str,
        user: str,
        tier: Literal["fast", "reasoning"] = "fast",
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        if self.primary is None:
            raise LLMProviderError("No LLM provider is configured (both GROQ_API_KEY and OPENROUTER_API_KEY are None).")

        primary_is_groq = self._primary_is_groq
        primary_model = self._model_for_client(primary_is_groq, tier)

        last_primary_exc: Exception | None = None
        for attempt in range(MAX_RETRIES_ON_FAILURE + 1):
            try:
                result = self._call_client(
                    self.primary, primary_model, system, user, temperature, max_tokens
                )
                return result
            except Exception as exc:
                last_primary_exc = exc
                is_rate_limit = "429" in str(exc) or "rate_limit" in str(exc).lower()
                if attempt < MAX_RETRIES_ON_FAILURE:
                    backoff = 2 ** attempt  # 1s, 2s, 4s
                    logger.warning(
                        "Primary provider %s attempt %d/%d failed%s. Retrying in %ds. Error: %s",
                        self.primary_name,
                        attempt + 1,
                        MAX_RETRIES_ON_FAILURE + 1,
                        " (rate limit)" if is_rate_limit else "",
                        backoff,
                        exc,
                    )
                    time.sleep(backoff)
                else:
                    logger.error(
                        "Primary provider %s exhausted all %d attempts. Last error: %s",
                        self.primary_name,
                        MAX_RETRIES_ON_FAILURE + 1,
                        exc,
                    )

        if self.fallback is not None:
            fallback_is_groq = not primary_is_groq
            fallback_model = self._model_for_client(fallback_is_groq, tier)
            logger.warning(
                "Switching from primary provider %s to fallback provider %s (model: %s).",
                self.primary_name,
                self.fallback_name,
                fallback_model,
            )
            try:
                result = self._call_client(
                    self.fallback, fallback_model, system, user, temperature, max_tokens
                )
                return result
            except Exception as exc:
                logger.error(
                    "Fallback provider %s also failed. Error: %s",
                    self.fallback_name,
                    exc,
                )
                raise LLMProviderError(
                    f"Both primary ({self.primary_name}) and fallback ({self.fallback_name}) providers failed. "
                    f"Primary error: {last_primary_exc}. Fallback error: {exc}."
                ) from exc

        raise LLMProviderError(
            f"Primary provider {self.primary_name} failed after all retries and no fallback is configured. "
            f"Last error: {last_primary_exc}."
        ) from last_primary_exc

    @staticmethod
    def _strip_fences(text: str) -> str:
        """Strip markdown code fences from an LLM response, including any preamble."""
        text = text.strip()
        fence_idx = text.find("```")
        if fence_idx == -1:
            return text
        # Slice from the opening fence, take content between first and second fence
        after_open = text[fence_idx + 3:]
        # Strip optional language tag (e.g. "json\n")
        if after_open.startswith("json"):
            after_open = after_open[4:]
        # Content ends at the next closing fence
        close_idx = after_open.find("```")
        if close_idx != -1:
            after_open = after_open[:close_idx]
        return after_open.strip()

    def chat_json(
        self,
        system: str,
        user: str,
        tier: Literal["fast", "reasoning"] = "fast",
    ) -> dict | list:
        json_instruction = "Respond ONLY with valid JSON. No markdown fences, no preamble, no explanation."
        augmented_system = f"{system}\n{json_instruction}"

        raw_response = self.chat(system=augmented_system, user=user, tier=tier)

        try:
            return json.loads(self._strip_fences(raw_response))
        except json.JSONDecodeError:
            logger.warning(
                "First JSON parse attempt failed. Retrying with stricter prompt. Raw response: %r",
                raw_response,
            )

        strict_instruction = (
            "Your previous response was not valid JSON. Return ONLY raw JSON, nothing else."
        )
        retry_system = f"{system}\n{json_instruction}\n{strict_instruction}"

        raw_retry_response = self.chat(system=retry_system, user=user, tier=tier)

        try:
            return json.loads(self._strip_fences(raw_retry_response))
        except json.JSONDecodeError as exc:
            logger.error(
                "Second JSON parse attempt also failed. Raw response: %r",
                raw_retry_response,
            )
            raise LLMParseError(
                f"Failed to parse JSON after two attempts. Raw response from second attempt: {raw_retry_response!r}"
            ) from exc


if __name__ == "__main__":
    import sys
    import os

    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")

    client = LLMClient()
    try:
        result = client.chat_json(
            system="You are a test assistant.",
            user="Return a JSON object with key 'status' and value 'ok'.",
            tier="fast",
        )
        print(result)
    except LLMProviderError as exc:
        print(f"Provider error: {exc}")
    except LLMParseError as exc:
        print(f"Parse error: {exc}")
    except Exception as exc:
        print(f"Unexpected error: {exc}")
