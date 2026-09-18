"""
CareerOS Semantic Embeddings & Dense Vector Storage Engine
===========================================================
Generates 768-dimensional dense vector embeddings using Google GenAI (text-embedding-004)
and stores them as packed float32 BLOBs directly in SQLite WAL (careeros.db).
Performs pure-Python zero-dependency cosine similarity search with dot-product ranking.
"""

import os
import math
import struct
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any, Union
from dotenv import load_dotenv

from engine.storage.db import get_db_connection

logger = logging.getLogger("careeros.embeddings")

_ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(_ROOT_DIR / ".env")

VECTOR_DIMENSION = 768

class EmbeddingsEngine:
    """Manages dense vector generation, persistence, and cosine similarity retrieval."""

    _client = None
    _cache: Dict[str, List[float]] = {}

    @classmethod
    def _get_client(cls):
        if cls._client is None:
            try:
                from google import genai
                cls._client = genai.Client()
            except Exception as e:
                logger.warning(f"Failed to initialize Google GenAI Client for embeddings: {e}")
                cls._client = None
        return cls._client

    @classmethod
    def generate_embedding(cls, text: str, model: str = "text-embedding-004") -> List[float]:
        """
        Generates a 768-dim float vector for input text.
        Falls back to a deterministic normalized pseudo-semantic vector if offline.
        """
        clean_text = (text or "").strip()
        if not clean_text:
            return [0.0] * VECTOR_DIMENSION

        if clean_text in cls._cache:
            return cls._cache[clean_text]

        client = cls._get_client()
        if client:
            try:
                res = client.models.embed_content(
                    model=model,
                    contents=clean_text[:8000]
                )
                if res and res.embeddings and len(res.embeddings) > 0:
                    vec = list(res.embeddings[0].values)
                    if len(vec) == VECTOR_DIMENSION:
                        cls._cache[clean_text] = vec
                        return vec
            except Exception as e:
                logger.warning(f"[EmbeddingsEngine] API embedding failed, using fallback: {e}")

        # Deterministic offline fallback embedding based on token hashing
        fallback_vec = cls._deterministic_fallback_vector(clean_text)
        cls._cache[clean_text] = fallback_vec
        return fallback_vec

    @classmethod
    def _deterministic_fallback_vector(cls, text: str) -> List[float]:
        """Produces a deterministic normalized 768-dim float vector from text tokens."""
        import hashlib
        import re
        tokens = re.findall(r"\w+", text.lower())
        vec = [0.0] * VECTOR_DIMENSION
        if not tokens:
            return vec
        for t in tokens:
            h = int(hashlib.md5(t.encode("utf-8")).hexdigest(), 16)
            idx = h % VECTOR_DIMENSION
            weight = 1.0 + (h % 10) / 10.0
            vec[idx] += weight

        # Normalize to unit length
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    @staticmethod
    def pack_vector(vector: List[float]) -> bytes:
        """Packs a list of floats into binary float32 bytes."""
        return struct.pack(f"{len(vector)}f", *vector)

    @staticmethod
    def unpack_vector(blob: bytes) -> List[float]:
        """Unpacks binary float32 bytes into a list of floats."""
        count = len(blob) // 4
        return list(struct.unpack(f"{count}f", blob))

    @staticmethod
    def compute_cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        """Computes cosine similarity between two float vectors (-1.0 to 1.0)."""
        if len(vec_a) != len(vec_b) or not vec_a:
            return 0.0
        
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(dot / (norm_a * norm_b))

    @classmethod
    def index_talent_profile(
        cls,
        profile_id: str,
        anonymized_alias: str,
        semantic_text: str,
        vector: Optional[List[float]] = None
    ) -> List[float]:
        """Indexes an anonymized candidate profile into talent_embeddings."""
        vec = vector or cls.generate_embedding(semantic_text)
        blob = cls.pack_vector(vec)
        now = datetime.now(timezone.utc).isoformat()

        with get_db_connection() as conn:
            conn.execute("""
            INSERT OR REPLACE INTO talent_embeddings (profile_id, anonymized_alias, embedding_blob, raw_text_chunk, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """, (profile_id, anonymized_alias, blob, semantic_text[:3000], now))

        logger.info(f"[EmbeddingsEngine] Indexed candidate vector: {anonymized_alias} ({profile_id})")
        return vec

    @classmethod
    def index_requisition(
        cls,
        req_id: str,
        job_title: str,
        jd_text: str,
        vector: Optional[List[float]] = None
    ) -> List[float]:
        """Indexes a recruiter job requisition into requisition_embeddings."""
        combined = f"Title: {job_title}\n\n{jd_text}"
        vec = vector or cls.generate_embedding(combined)
        blob = cls.pack_vector(vec)
        now = datetime.now(timezone.utc).isoformat()

        with get_db_connection() as conn:
            conn.execute("""
            INSERT OR REPLACE INTO requisition_embeddings (req_id, job_title, embedding_blob, raw_text_chunk, created_at)
            VALUES (?, ?, ?, ?, ?)
            """, (req_id, job_title, blob, combined[:3000], now))

        logger.info(f"[EmbeddingsEngine] Indexed requisition vector: {job_title} ({req_id})")
        return vec

    @classmethod
    def search_talent_semantic(
        cls,
        query_text_or_vector: Union[str, List[float]],
        top_k: int = 5,
        min_similarity: float = 0.4
    ) -> List[Dict[str, Any]]:
        """
        Executes semantic vector similarity search against all talent_embeddings in SQLite.
        Returns ranked list of candidate matches.
        """
        if isinstance(query_text_or_vector, str):
            query_vec = cls.generate_embedding(query_text_or_vector)
        else:
            query_vec = query_text_or_vector

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT profile_id, anonymized_alias, embedding_blob, raw_text_chunk FROM talent_embeddings")
            rows = cursor.fetchall()

        results = []
        for r in rows:
            blob = r["embedding_blob"]
            cand_vec = cls.unpack_vector(blob)
            sim = cls.compute_cosine_similarity(query_vec, cand_vec)
            if sim >= min_similarity:
                results.append({
                    "profile_id": r["profile_id"],
                    "anonymized_alias": r["anonymized_alias"],
                    "semantic_similarity": round(sim, 4),
                    "raw_text_chunk": r["raw_text_chunk"]
                })

        results.sort(key=lambda x: x["semantic_similarity"], reverse=True)
        return results[:top_k]

    @classmethod
    def seed_default_embeddings_if_empty(cls):
        """Pre-indexes candidate profiles from talent_lake if talent_embeddings is empty."""
        from engine.talent_graph.store import TalentLakeStore
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM talent_embeddings")
            count = cursor.fetchone()[0]

        if count == 0:
            TalentLakeStore.seed_default_talent_pool()
            profiles = TalentLakeStore.list_profiles()
            for p in profiles:
                proofs = " ".join([f"{m.label}: {m.evidence}" for m in p.verified_proof_metrics])
                govs = ", ".join(p.governance_tags)
                semantic_chunk = (
                    f"Headline: {p.headline}. Seniority: {p.seniority}. "
                    f"Roles: {', '.join(p.target_roles)}. Competencies: {', '.join(p.core_competencies)}. "
                    f"Governance: {govs}. Verified Proofs: {proofs}"
                )
                cls.index_talent_profile(
                    profile_id=p.profile_id,
                    anonymized_alias=p.anonymized_alias,
                    semantic_text=semantic_chunk
                )
