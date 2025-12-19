"""
SQLite storage layer for the Roots Service.
"""

import uuid
from datetime import datetime
from typing import Optional

from common.database import DatabaseManager, get_db_path, json_serialize, json_deserialize
from common.logging_config import get_logger
from common.exceptions import NotFoundError, DatabaseError

from .models import Root, RootCreate, RootUpdate, RootType, RootSummary

logger = get_logger(__name__)

# Database schema
ROOTS_SCHEMA = """
CREATE TABLE IF NOT EXISTS roots (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    root_type TEXT NOT NULL CHECK(root_type IN ('EXTANT', 'ABSTRACT', 'MENTAL', 'FICTIVE')),
    description TEXT,
    metadata TEXT,
    import_source TEXT,
    ai_enhancement_trace TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_roots_type ON roots(root_type);
CREATE INDEX IF NOT EXISTS idx_roots_created ON roots(created_at);
CREATE INDEX IF NOT EXISTS idx_roots_name ON roots(name);
"""


class RootsStore:
    """
    SQLite storage layer for root entities.
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the roots store.

        Args:
            db_path: Path to SQLite database (defaults to configured path)
        """
        if db_path is None:
            db_path = get_db_path("roots.db")
        self.db = DatabaseManager(db_path)
        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize database schema."""
        try:
            self.db.execute_script(ROOTS_SCHEMA)
            logger.info("Roots database schema initialized")
        except Exception as e:
            logger.error(f"Failed to initialize schema: {e}")
            raise DatabaseError("Failed to initialize database schema", str(e))

    def _row_to_root(self, row: dict) -> Root:
        """Convert database row to Root model."""
        return Root(
            id=row["id"],
            name=row["name"],
            root_type=RootType(row["root_type"]),
            description=row.get("description"),
            metadata=json_deserialize(row.get("metadata")),
            import_source=row.get("import_source"),
            ai_enhancement_trace=row.get("ai_enhancement_trace"),
            created_at=datetime.fromisoformat(row["created_at"]) if isinstance(row["created_at"], str) else row["created_at"],
            updated_at=datetime.fromisoformat(row["updated_at"]) if isinstance(row["updated_at"], str) else row["updated_at"],
        )

    def create(self, root_data: RootCreate) -> Root:
        """
        Create a new root entity.

        Args:
            root_data: Root creation data

        Returns:
            Created Root entity
        """
        root_id = str(uuid.uuid4())
        now = datetime.utcnow()

        query = """
            INSERT INTO roots (id, name, root_type, description, metadata, import_source, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            root_id,
            root_data.name,
            root_data.root_type.value,
            root_data.description,
            json_serialize(root_data.metadata),
            root_data.import_source,
            now.isoformat(),
            now.isoformat(),
        )

        self.db.execute_write(query, params)
        logger.info(f"Created root: {root_id}")

        return self.get_by_id(root_id)

    def get_by_id(self, root_id: str) -> Root:
        """
        Get a root by ID.

        Args:
            root_id: Root ID

        Returns:
            Root entity

        Raises:
            NotFoundError: If root not found
        """
        query = "SELECT * FROM roots WHERE id = ?"
        row = self.db.execute_one(query, (root_id,))

        if not row:
            raise NotFoundError("Root", root_id)

        return self._row_to_root(row)

    def get_all(
        self,
        offset: int = 0,
        limit: int = 50,
        root_type: Optional[RootType] = None,
    ) -> tuple[list[Root], int]:
        """
        Get all roots with pagination.

        Args:
            offset: Number of items to skip
            limit: Maximum items to return
            root_type: Optional filter by root type

        Returns:
            Tuple of (roots list, total count)
        """
        # Build query based on filters
        where_clause = ""
        params = []

        if root_type:
            where_clause = "WHERE root_type = ?"
            params.append(root_type.value)

        # Get total count
        count_query = f"SELECT COUNT(*) as count FROM roots {where_clause}"
        count_result = self.db.execute_one(count_query, tuple(params) if params else None)
        total = count_result["count"] if count_result else 0

        # Get paginated results
        query = f"""
            SELECT * FROM roots {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        rows = self.db.execute(query, tuple(params))

        roots = [self._row_to_root(row) for row in rows]
        return roots, total

    def update(self, root_id: str, update_data: RootUpdate) -> Root:
        """
        Update a root entity.

        Args:
            root_id: Root ID
            update_data: Update data

        Returns:
            Updated Root entity

        Raises:
            NotFoundError: If root not found
        """
        # First check if root exists
        existing = self.get_by_id(root_id)

        # Build update query
        updates = []
        params = []

        if update_data.name is not None:
            updates.append("name = ?")
            params.append(update_data.name)
        if update_data.root_type is not None:
            updates.append("root_type = ?")
            params.append(update_data.root_type.value)
        if update_data.description is not None:
            updates.append("description = ?")
            params.append(update_data.description)
        if update_data.metadata is not None:
            updates.append("metadata = ?")
            params.append(json_serialize(update_data.metadata))

        if not updates:
            return existing

        updates.append("updated_at = ?")
        params.append(datetime.utcnow().isoformat())
        params.append(root_id)

        query = f"UPDATE roots SET {', '.join(updates)} WHERE id = ?"
        self.db.execute_write(query, tuple(params))

        logger.info(f"Updated root: {root_id}")
        return self.get_by_id(root_id)

    def delete(self, root_id: str) -> bool:
        """
        Delete a root entity.

        Args:
            root_id: Root ID

        Returns:
            True if deleted

        Raises:
            NotFoundError: If root not found
        """
        # First check if root exists
        self.get_by_id(root_id)

        query = "DELETE FROM roots WHERE id = ?"
        self.db.execute_write(query, (root_id,))

        logger.info(f"Deleted root: {root_id}")
        return True

    def get_summary(self) -> RootSummary:
        """
        Get summary statistics for roots.

        Returns:
            RootSummary with statistics
        """
        # Get total count
        count_query = "SELECT COUNT(*) as count FROM roots"
        count_result = self.db.execute_one(count_query)
        total = count_result["count"] if count_result else 0

        # Get counts by type
        type_query = """
            SELECT root_type, COUNT(*) as count
            FROM roots
            GROUP BY root_type
        """
        type_rows = self.db.execute(type_query)
        by_type = {row["root_type"]: row["count"] for row in type_rows}

        # Ensure all types are represented
        for root_type in RootType:
            if root_type.value not in by_type:
                by_type[root_type.value] = 0

        return RootSummary(total_count=total, by_type=by_type)

    def get_by_type(self, root_type: RootType, offset: int = 0, limit: int = 50) -> tuple[list[Root], int]:
        """
        Get roots by type.

        Args:
            root_type: Root type to filter by
            offset: Number of items to skip
            limit: Maximum items to return

        Returns:
            Tuple of (roots list, total count)
        """
        return self.get_all(offset=offset, limit=limit, root_type=root_type)
