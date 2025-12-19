"""
SQLite database utilities for OmniCore services.
"""

import os
import sqlite3
import json
from typing import Optional, Any
from contextlib import contextmanager
from pathlib import Path

from .logging_config import get_logger
from .config import settings

logger = get_logger(__name__)


def get_db_path(db_name: str) -> str:
    """
    Get the full path to a database file.

    Args:
        db_name: Database filename (e.g., "roots.db")

    Returns:
        Full path to the database file
    """
    db_dir = settings.database_path
    Path(db_dir).mkdir(parents=True, exist_ok=True)
    return os.path.join(db_dir, db_name)


class DatabaseManager:
    """
    SQLite database manager with connection pooling and utilities.
    """

    def __init__(self, db_path: str):
        """
        Initialize database manager.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._ensure_db_directory()

    def _ensure_db_directory(self) -> None:
        """Ensure the database directory exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            Path(db_dir).mkdir(parents=True, exist_ok=True)

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.

        Yields:
            sqlite3.Connection: Database connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def execute(
        self,
        query: str,
        params: Optional[tuple] = None,
    ) -> list[dict]:
        """
        Execute a query and return results as list of dicts.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of result rows as dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if cursor.description:
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            return []

    def execute_one(
        self,
        query: str,
        params: Optional[tuple] = None,
    ) -> Optional[dict]:
        """
        Execute a query and return a single result.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Single result row as dictionary or None
        """
        results = self.execute(query, params)
        return results[0] if results else None

    def execute_write(
        self,
        query: str,
        params: Optional[tuple] = None,
    ) -> int:
        """
        Execute an INSERT/UPDATE/DELETE query.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Number of affected rows
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.rowcount

    def execute_script(self, script: str) -> None:
        """
        Execute a multi-statement SQL script.

        Args:
            script: SQL script string
        """
        with self.get_connection() as conn:
            conn.executescript(script)

    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.

        Args:
            table_name: Name of the table

        Returns:
            True if table exists, False otherwise
        """
        query = """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name=?
        """
        result = self.execute_one(query, (table_name,))
        return result is not None


def json_serialize(data: Any) -> Optional[str]:
    """Serialize data to JSON string."""
    if data is None:
        return None
    return json.dumps(data)


def json_deserialize(data: Optional[str]) -> Any:
    """Deserialize JSON string to data."""
    if data is None:
        return None
    return json.loads(data)
