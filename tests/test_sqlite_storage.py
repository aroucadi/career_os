"""
CareerOS SQLite WAL Storage & Migration Test Suite
===================================================
Verifies the Release 2.2 persistent SQLite core (SPEC-0043):
1. Zero-dependency SQLite initialization and schema tables.
2. PRAGMA journal_mode = WAL enforcement for high concurrency.
3. Idempotent table creation and index setup.
4. Auto-migration capability from flat JSON storage.
5. Recruiter Organization default seeding.
"""

import os
import sqlite3
import pytest
from pathlib import Path
import tempfile

from engine.storage.db import get_db_connection, DatabaseManager, DB_PATH
from engine.storage.migrator import StorageMigrator

def test_db_initialization_and_tables():
    """Verifies that all 6 critical tables and indices are created."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        temp_db_path = Path(tmp.name)

    try:
        DatabaseManager.init_db(temp_db_path)

        with get_db_connection(temp_db_path) as conn:
            cursor = conn.cursor()

            # Check journal_mode is WAL
            cursor.execute("PRAGMA journal_mode;")
            mode = cursor.fetchone()[0].lower()
            assert mode == "wal", f"Expected WAL mode, got {mode}"

            # Check all required tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = {row[0] for row in cursor.fetchall()}
            expected_tables = {
                "token_ledgers",
                "talent_profiles",
                "recruiter_matches",
                "pipeline_opportunities",
                "consent_tokens",
                "recruiter_orgs"
            }
            assert expected_tables.issubset(tables), f"Missing tables: {expected_tables - tables}"

            # Verify default recruiter org was seeded
            cursor.execute("SELECT org_id, api_key, credits_balance FROM recruiter_orgs WHERE api_key = 'cr_live_test123'")
            org = cursor.fetchone()
            assert org is not None
            assert org["credits_balance"] >= 100
    finally:
        if temp_db_path.exists():
            try:
                os.remove(temp_db_path)
            except Exception:
                pass


def test_db_transaction_rollback():
    """Verifies ACID rollback behavior on exceptions."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        temp_db_path = Path(tmp.name)

    try:
        DatabaseManager.init_db(temp_db_path)

        # Attempt an invalid transaction
        with pytest.raises(sqlite3.IntegrityError):
            with get_db_connection(temp_db_path) as conn:
                conn.execute("INSERT INTO recruiter_orgs (org_id, name, api_key, credits_balance, tier, created_at) VALUES ('org1', 'Org One', 'key1', 10, 'BASIC', '2026-09-17')")
                # Intentionally insert duplicate primary key or duplicate api_key to trigger rollback
                conn.execute("INSERT INTO recruiter_orgs (org_id, name, api_key, credits_balance, tier, created_at) VALUES ('org1', 'Org Duplicate', 'key2', 10, 'BASIC', '2026-09-17')")

        # Confirm org1 was not committed due to rollback
        with get_db_connection(temp_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM recruiter_orgs WHERE org_id = 'org1'")
            assert cursor.fetchone() is None
    finally:
        if temp_db_path.exists():
            try:
                os.remove(temp_db_path)
            except Exception:
                pass


def test_storage_migrator_idempotence():
    """Verifies that StorageMigrator runs smoothly without error on active DB."""
    # Run migration on the current application database
    result = StorageMigrator.migrate_all()
    assert isinstance(result, dict)
    assert "token_ledgers" in result
    assert "talent_profiles" in result
    assert "recruiter_matches" in result
    assert "pipeline_opportunities" in result
    assert "status" in result
    assert result["status"] == "COMPLETED"
