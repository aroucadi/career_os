"""
CareerOS Semantic Embeddings & Dense Vector Storage Test Suite
===============================================================
Verifies 768-dim float32 vector serialization, pure-Python cosine similarity,
SQLite BLOB persistence, and semantic talent search.
"""

import os
import math
import struct
import pytest
from engine.storage.embeddings import EmbeddingsEngine, VECTOR_DIMENSION
from engine.storage.db import get_db_connection, DatabaseManager

@pytest.fixture(autouse=True)
def setup_db():
    DatabaseManager.init_db()

def test_vector_packing_and_unpacking():
    original = [0.12345, -0.98765, 0.0, 1.0, -1.0] * 150 # 750 elements
    original.extend([0.5, 0.25, -0.75] * 6) # 768 elements
    assert len(original) == VECTOR_DIMENSION

    packed = EmbeddingsEngine.pack_vector(original)
    assert len(packed) == VECTOR_DIMENSION * 4 # 768 * 4 bytes = 3072 bytes

    unpacked = EmbeddingsEngine.unpack_vector(packed)
    assert len(unpacked) == VECTOR_DIMENSION
    for a, b in zip(original, unpacked):
        assert abs(a - b) < 1e-5

def test_cosine_similarity_math():
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [1.0, 0.0, 0.0]
    vec3 = [0.0, 1.0, 0.0]
    vec4 = [-1.0, 0.0, 0.0]

    assert abs(EmbeddingsEngine.compute_cosine_similarity(vec1, vec2) - 1.0) < 1e-6
    assert abs(EmbeddingsEngine.compute_cosine_similarity(vec1, vec3) - 0.0) < 1e-6
    assert abs(EmbeddingsEngine.compute_cosine_similarity(vec1, vec4) - (-1.0)) < 1e-6

def test_generate_embedding_dimension():
    text = "Senior AI Product & Delivery Manager specializing in EU AI Act governance."
    vec = EmbeddingsEngine.generate_embedding(text)
    assert isinstance(vec, list)
    assert len(vec) == VECTOR_DIMENSION
    norm = math.sqrt(sum(x * x for x in vec))
    assert abs(norm - 1.0) < 0.01 # Normalized vector

def test_talent_vector_indexing_and_search():
    # Index 2 distinct candidate vectors
    p1_id = "test_cand_ai"
    p1_alias = "Candidate #AI01 — AI Delivery Lead"
    p1_text = "Experienced AI Delivery Lead scaling GenAI agents, Atlassian Rovo, and EU AI Act compliance in banking."

    p2_id = "test_cand_audit"
    p2_alias = "Candidate #AU02 — SOX IT Auditor"
    p2_text = "Director of Internal Audit leading SOX 404 automation, risk controls, and ITGC financial audits."

    EmbeddingsEngine.index_talent_profile(p1_id, p1_alias, p1_text)
    EmbeddingsEngine.index_talent_profile(p2_id, p2_alias, p2_text)

    # Search query specifically for AI Delivery
    results = EmbeddingsEngine.search_talent_semantic("AI Delivery Lead with EU AI Act banking experience", top_k=2)
    assert len(results) >= 1
    top = results[0]
    assert top["profile_id"] == p1_id
    assert top["semantic_similarity"] > 0.4
