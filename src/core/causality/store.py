"""
SQLite storage layer for the Causality Service.
"""

import uuid
from datetime import datetime
from typing import Optional

from common.database import DatabaseManager, get_db_path, json_serialize, json_deserialize
from common.logging_config import get_logger
from common.exceptions import NotFoundError, DatabaseError

from .models import CausalityLink, CausalityLinkCreate, CausalityLinkUpdate, CausalityType, CausalitySummary

logger = get_logger(__name__)

# Database schema
CAUSALITY_SCHEMA = """
CREATE TABLE IF NOT EXISTS causality_links (
    id TEXT PRIMARY KEY,
    source_entity_id TEXT NOT NULL,
    target_entity_id TEXT NOT NULL,
    causality_type TEXT NOT NULL CHECK(causality_type IN ('EFFICIENT', 'FINAL', 'MATERIAL', 'FORMAL', 'EMERGENT')),
    confidence REAL DEFAULT 1.0 CHECK(confidence >= 0.0 AND confidence <= 1.0),
    description TEXT,
    metadata TEXT,
    ai_confidence REAL,
    rationale_trace TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_causality_type ON causality_links(causality_type);
CREATE INDEX IF NOT EXISTS idx_causality_source ON causality_links(source_entity_id);
CREATE INDEX IF NOT EXISTS idx_causality_target ON causality_links(target_entity_id);
CREATE INDEX IF NOT EXISTS idx_causality_confidence ON causality_links(confidence);
"""


class CausalityStore:
    """
    SQLite storage layer for causality links.
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the causality store.

        Args:
            db_path: Path to SQLite database (defaults to configured path)
        """
        if db_path is None:
            db_path = get_db_path("causality.db")
        self.db = DatabaseManager(db_path)
        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize database schema."""
        try:
            self.db.execute_script(CAUSALITY_SCHEMA)
            logger.info("Causality database schema initialized")
        except Exception as e:
            logger.error(f"Failed to initialize schema: {e}")
            raise DatabaseError("Failed to initialize database schema", str(e))

    def _row_to_link(self, row: dict) -> CausalityLink:
        """Convert database row to CausalityLink model."""
        return CausalityLink(
            id=row["id"],
            source_entity_id=row["source_entity_id"],
            target_entity_id=row["target_entity_id"],
            causality_type=CausalityType(row["causality_type"]),
            confidence=row["confidence"],
            description=row.get("description"),
            metadata=json_deserialize(row.get("metadata")),
            ai_confidence=row.get("ai_confidence"),
            rationale_trace=row.get("rationale_trace"),
            created_at=datetime.fromisoformat(row["created_at"]) if isinstance(row["created_at"], str) else row["created_at"],
            updated_at=datetime.fromisoformat(row["updated_at"]) if isinstance(row["updated_at"], str) else row["updated_at"],
        )

    def create(self, link_data: CausalityLinkCreate) -> CausalityLink:
        """
        Create a new causality link.

        Args:
            link_data: Link creation data

        Returns:
            Created CausalityLink entity
        """
        link_id = str(uuid.uuid4())
        now = datetime.utcnow()

        query = """
            INSERT INTO causality_links
            (id, source_entity_id, target_entity_id, causality_type, confidence, description, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            link_id,
            link_data.source_entity_id,
            link_data.target_entity_id,
            link_data.causality_type.value,
            link_data.confidence,
            link_data.description,
            json_serialize(link_data.metadata),
            now.isoformat(),
            now.isoformat(),
        )

        self.db.execute_write(query, params)
        logger.info(f"Created causality link: {link_id}")

        return self.get_by_id(link_id)

    def get_by_id(self, link_id: str) -> CausalityLink:
        """
        Get a causality link by ID.

        Args:
            link_id: Link ID

        Returns:
            CausalityLink entity

        Raises:
            NotFoundError: If link not found
        """
        query = "SELECT * FROM causality_links WHERE id = ?"
        row = self.db.execute_one(query, (link_id,))

        if not row:
            raise NotFoundError("CausalityLink", link_id)

        return self._row_to_link(row)

    def get_all(
        self,
        offset: int = 0,
        limit: int = 50,
        causality_type: Optional[CausalityType] = None,
    ) -> tuple[list[CausalityLink], int]:
        """
        Get all causality links with pagination.

        Args:
            offset: Number of items to skip
            limit: Maximum items to return
            causality_type: Optional filter by type

        Returns:
            Tuple of (links list, total count)
        """
        where_clause = ""
        params = []

        if causality_type:
            where_clause = "WHERE causality_type = ?"
            params.append(causality_type.value)

        # Get total count
        count_query = f"SELECT COUNT(*) as count FROM causality_links {where_clause}"
        count_result = self.db.execute_one(count_query, tuple(params) if params else None)
        total = count_result["count"] if count_result else 0

        # Get paginated results
        query = f"""
            SELECT * FROM causality_links {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        rows = self.db.execute(query, tuple(params))

        links = [self._row_to_link(row) for row in rows]
        return links, total

    def update(self, link_id: str, update_data: CausalityLinkUpdate) -> CausalityLink:
        """
        Update a causality link.

        Args:
            link_id: Link ID
            update_data: Update data

        Returns:
            Updated CausalityLink entity

        Raises:
            NotFoundError: If link not found
        """
        existing = self.get_by_id(link_id)

        updates = []
        params = []

        if update_data.source_entity_id is not None:
            updates.append("source_entity_id = ?")
            params.append(update_data.source_entity_id)
        if update_data.target_entity_id is not None:
            updates.append("target_entity_id = ?")
            params.append(update_data.target_entity_id)
        if update_data.causality_type is not None:
            updates.append("causality_type = ?")
            params.append(update_data.causality_type.value)
        if update_data.confidence is not None:
            updates.append("confidence = ?")
            params.append(update_data.confidence)
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
        params.append(link_id)

        query = f"UPDATE causality_links SET {', '.join(updates)} WHERE id = ?"
        self.db.execute_write(query, tuple(params))

        logger.info(f"Updated causality link: {link_id}")
        return self.get_by_id(link_id)

    def delete(self, link_id: str) -> bool:
        """
        Delete a causality link.

        Args:
            link_id: Link ID

        Returns:
            True if deleted

        Raises:
            NotFoundError: If link not found
        """
        self.get_by_id(link_id)

        query = "DELETE FROM causality_links WHERE id = ?"
        self.db.execute_write(query, (link_id,))

        logger.info(f"Deleted causality link: {link_id}")
        return True

    def get_summary(self) -> CausalitySummary:
        """
        Get summary statistics for causality links.

        Returns:
            CausalitySummary with statistics
        """
        # Get total count
        count_query = "SELECT COUNT(*) as count FROM causality_links"
        count_result = self.db.execute_one(count_query)
        total = count_result["count"] if count_result else 0

        # Get counts by type
        type_query = """
            SELECT causality_type, COUNT(*) as count
            FROM causality_links
            GROUP BY causality_type
        """
        type_rows = self.db.execute(type_query)
        by_type = {row["causality_type"]: row["count"] for row in type_rows}

        # Ensure all types are represented
        for ctype in CausalityType:
            if ctype.value not in by_type:
                by_type[ctype.value] = 0

        # Get average confidence
        avg_query = "SELECT AVG(confidence) as avg_conf FROM causality_links"
        avg_result = self.db.execute_one(avg_query)
        avg_confidence = avg_result["avg_conf"] if avg_result and avg_result["avg_conf"] else 0.0

        return CausalitySummary(
            total_count=total,
            by_type=by_type,
            avg_confidence=round(avg_confidence, 4),
        )

    def get_by_entity(
        self,
        entity_id: str,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[CausalityLink], int]:
        """
        Get causality links involving a specific entity.

        Args:
            entity_id: Entity ID (source or target)
            offset: Number of items to skip
            limit: Maximum items to return

        Returns:
            Tuple of (links list, total count)
        """
        where_clause = "WHERE source_entity_id = ? OR target_entity_id = ?"
        params = [entity_id, entity_id]

        # Get total count
        count_query = f"SELECT COUNT(*) as count FROM causality_links {where_clause}"
        count_result = self.db.execute_one(count_query, tuple(params))
        total = count_result["count"] if count_result else 0

        # Get paginated results
        query = f"""
            SELECT * FROM causality_links {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        rows = self.db.execute(query, tuple(params))

        links = [self._row_to_link(row) for row in rows]
        return links, total
