"""OpenRouter chat client with streaming support."""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator
from typing import Any

import httpx
from openai import AsyncOpenAI

from ais_os.config import get_config

logger = logging.getLogger("ais_os.models.openrouter")


class OpenRouterClient:
    """Async chat client using OpenAI SDK pointed at OpenRouter."""

    def __init__(self) -> None:
        cfg = get_config()
        self._default_model = cfg.default_model
        api_key = cfg.openrouter_api_key
        if not api_key:
            logger.warning("OPENROUTER_API_KEY not set — chat will fail until configured")

        self._client = AsyncOpenAI(
            base_url=cfg.openrouter_base_url,
            api_key=api_key or "missing",
            default_headers={
                "HTTP-Referer": "https://github.com/nateherkai/AIS-OS",
                "X-Title": "AIS-OS Terminal",
            },
        )
        self._ollama_url = cfg.env.ollama_base_url
        self._ollama_key = cfg.env.ollama_api_key

    @property
    def default_model(self) -> str:
        return self._default_model

    def _resolve_client_and_model(self, model: str) -> tuple[AsyncOpenAI, str]:
        if model.startswith("ollama/"):
            local_name = model.split("/", 1)[1]
            return (
                AsyncOpenAI(base_url=self._ollama_url, api_key=self._ollama_key),
                local_name,
            )
        return self._client, model

    async def chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        temperature: float = 0.4,
        max_tokens: int = 4096,
        tools: list[dict[str, Any]] | None = None,
    ) -> str:
        use_model = model or self._default_model
        client, resolved = self._resolve_client_and_model(use_model)
        kwargs: dict[str, Any] = {
            "model": resolved,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        try:
            resp = await client.chat.completions.create(**kwargs)
            choice = resp.choices[0]
            if choice.message.tool_calls:
                return json.dumps(
                    [
                        {
                            "id": tc.id,
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        }
                        for tc in choice.message.tool_calls
                    ]
                )
            return choice.message.content or ""
        except Exception as exc:
            logger.exception("OpenRouter chat failed: %s", exc)
            raise

    async def stream_chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        temperature: float = 0.4,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        use_model = model or self._default_model
        client, resolved = self._resolve_client_and_model(use_model)
        try:
            stream = await client.chat.completions.create(
                model=resolved,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except httpx.HTTPError as exc:
            logger.exception("Stream HTTP error: %s", exc)
            raise
        except Exception as exc:
            logger.exception("Stream chat failed: %s", exc)
            raise

    async def embed(self, texts: list[str], model: str = "openai/text-embedding-3-small") -> list[list[float]]:
        """Embeddings via OpenRouter (requires API key)."""
        client, resolved = self._resolve_client_and_model(model)
        resp = await client.embeddings.create(model=resolved, input=texts)
        return [item.embedding for item in resp.data]
