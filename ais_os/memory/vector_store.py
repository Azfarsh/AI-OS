"""ChromaDB long-term vector memory."""

from __future__ import annotations

import hashlib
import logging
import uuid
from typing import Any

import chromadb
from chromadb.config import Settings

from ais_os.config import get_config
from ais_os.models.openrouter import OpenRouterClient

logger = logging.getLogger("ais_os.memory.vector")


class VectorMemoryStore:
    COLLECTION = "ais_os_memory"

    def __init__(self) -> None:
        cfg = get_config()
        cfg.chroma_path.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(
            path=str(cfg.chroma_path),
            settings=Settings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=self.COLLECTION,
            metadata={"hnsw:space": "cosine"},
        )
        self._embed_model = cfg.memory_settings.get(
            "embed_model", "openai/text-embedding-3-small"
        )
        self._llm = OpenRouterClient()

    async def _embed(self, texts: list[str]) -> list[list[float]]:
        try:
            return await self._llm.embed(texts, model=self._embed_model)
        except Exception as exc:
            logger.warning("Embedding API failed, using hash fallback: %s", exc)
            return [_hash_embed(t) for t in texts]

    async def add(
        self,
        text: str,
        *,
        metadata: dict[str, Any] | None = None,
        doc_id: str | None = None,
    ) -> str:
        doc_id = doc_id or str(uuid.uuid4())
        emb = (await self._embed([text]))[0]
        meta = metadata or {}
        meta.setdefault("source", "user")
        self._collection.upsert(
            ids=[doc_id],
            documents=[text],
            embeddings=[emb],
            metadatas=[{k: str(v) for k, v in meta.items()}],
        )
        return doc_id

    async def search(self, query: str, top_k: int = 6) -> list[dict[str, Any]]:
        emb = (await self._embed([query]))[0]
        result = self._collection.query(
            query_embeddings=[emb],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        hits: list[dict[str, Any]] = []
        if not result["documents"]:
            return hits
        for i, doc in enumerate(result["documents"][0]):
            hits.append(
                {
                    "text": doc,
                    "metadata": (result["metadatas"] or [{}])[0][i] if result["metadatas"] else {},
                    "distance": (result["distances"] or [[0]])[0][i],
                }
            )
        return hits

    def count(self) -> int:
        return self._collection.count()


def _hash_embed(text: str, dim: int = 384) -> list[float]:
    """Deterministic fallback when embeddings API unavailable."""
    digest = hashlib.sha256(text.encode()).digest()
    vals = [digest[i % len(digest)] / 255.0 for i in range(dim)]
    norm = sum(v * v for v in vals) ** 0.5 or 1.0
    return [v / norm for v in vals]
