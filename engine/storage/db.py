"""
CareerOS Zero-Dependency SQLite WAL Database Manager
====================================================
Provides ACID-compliant multi-process persistence utilizing Python's built-in sqlite3.
Enforces Write-Ahead Logging (WAL) for high concurrency and zero multi-worker desync.
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional, ContextManager
from contextlib import contextmanager

logger = logging.getLogger("careeros.storage")

DB_PATH = Path(__file__).resolve().parent.parent.parent / "storage" / "careeros.db"

def get_db_path() -> Path:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return DB_PATH

@contextmanager
def get_db_connection(db_path: Optional[Path] = None):
    """Context manager yielding a SQLite connection configured with WAL mode."""
    target_path = db_path or get_db_path()
    conn = sqlite3.connect(str(target_path), timeout=30.0)
    conn.row_factory = sqlite3.Row
    try:
        # Enforce WAL mode and concurrency pragmas
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        conn.execute("PRAGMA foreign_keys = ON;")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

class DatabaseManager:
    """Initializes schemas and manages SQLite operations."""

    @classmethod
    def init_db(cls, db_path: Optional[Path] = None):
        """Creates all required tables if they do not exist."""
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()

            # 1. Token Ledgers
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS token_ledgers (
                user_id TEXT PRIMARY KEY,
                balance_credits INTEGER NOT NULL DEFAULT 100,
                max_credits INTEGER NOT NULL DEFAULT 100,
                total_consumed INTEGER NOT NULL DEFAULT 0,
                data_json TEXT NOT NULL DEFAULT '{}',
                updated_at TEXT NOT NULL
            );
            """)

            # 2. Talent Intelligence Lake Profiles
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS talent_profiles (
                profile_id TEXT PRIMARY KEY,
                anonymized_alias TEXT NOT NULL,
                headline TEXT NOT NULL,
                seniority TEXT NOT NULL,
                readiness_status TEXT NOT NULL,
                verified_score REAL NOT NULL DEFAULT 85.0,
                governance_tags TEXT NOT NULL DEFAULT '[]',
                data_json TEXT NOT NULL DEFAULT '{}',
                indexed_at TEXT NOT NULL
            );
            """)

            # 3. Recruiter Requisition Matches
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS recruiter_matches (
                match_id TEXT PRIMARY KEY,
                candidate_id TEXT NOT NULL,
                job_title TEXT NOT NULL,
                overall_score REAL NOT NULL,
                opt_in_status TEXT NOT NULL DEFAULT 'PENDING_CONSENT',
                data_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL
            );
            """)

            # 4. Pipeline CRM Opportunities
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_opportunities (
                id TEXT PRIMARY KEY,
                job_title TEXT NOT NULL,
                company TEXT NOT NULL,
                stage TEXT NOT NULL,
                fit_score REAL NOT NULL DEFAULT 85.0,
                data_json TEXT NOT NULL DEFAULT '{}',
                updated_at TEXT NOT NULL
            );
            """)

            # 5. Double Opt-In Consent Tokens
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS consent_tokens (
                token TEXT PRIMARY KEY,
                match_id TEXT NOT NULL,
                candidate_id TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """)

            # 6. Recruiter Organizations & Monetization Ledger
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS recruiter_orgs (
                org_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                api_key TEXT UNIQUE NOT NULL,
                credits_balance INTEGER NOT NULL DEFAULT 100,
                tier TEXT NOT NULL DEFAULT 'STARTER',
                created_at TEXT NOT NULL
            );
            """)

            # 7. Dense Vector Talent Embeddings (768-dim float32 packed BLOBs)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS talent_embeddings (
                profile_id TEXT PRIMARY KEY,
                anonymized_alias TEXT NOT NULL,
                embedding_blob BLOB NOT NULL,
                raw_text_chunk TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """)

            # 8. Requisition Vector Embeddings
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS requisition_embeddings (
                req_id TEXT PRIMARY KEY,
                job_title TEXT NOT NULL,
                embedding_blob BLOB NOT NULL,
                raw_text_chunk TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """)

            # Create Indexes for fast querying
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_talent_status ON talent_profiles(readiness_status);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_matches_cand ON recruiter_matches(candidate_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_matches_status ON recruiter_matches(opt_in_status);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tokens_match ON consent_tokens(match_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_recruiter_key ON recruiter_orgs(api_key);")

            # Seed default development recruiter org if not present
            cursor.execute("SELECT org_id FROM recruiter_orgs WHERE api_key = 'cr_live_test123'")
            if not cursor.fetchone():
                cursor.execute("""
                INSERT INTO recruiter_orgs (org_id, name, api_key, credits_balance, tier, created_at)
                VALUES ('org_default_test', 'CareerOS Partner Headhunters', 'cr_live_test123', 500, 'ENTERPRISE', datetime('now'))
                """)

            logger.info("[DatabaseManager] SQLite WAL schema successfully verified.")
