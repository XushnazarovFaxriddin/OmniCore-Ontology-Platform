"""
SQLite storage layer for the Epistemic Service.
"""

import uuid
from datetime import datetime
from typing import Optional

from common.database import DatabaseManager, get_db_path
from common.logging_config import get_logger
from common.exceptions import NotFoundError, DatabaseError

from .models import EpistemicAnnotation, EpistemicAnnotationCreate, EpistemicAnnotationUpdate, EpistemicBasis, EpistemicSummary

logger = get_logger(__name__)

# Database schema
EPISTEMIC_SCHEMA = """
CREATE TABLE IF NOT EXISTS epistemic_annotations (
    id TEXT PRIMARY KEY,
    entity_id TEXT NOT NULL,
    certainty REAL NOT NULL CHECK(certainty >= 0.0 AND certainty <= 1.0),
    basis TEXT NOT NULL CHECK(basis IN ('axiomatic', 'empirical', 'consensus', 'speculative')),
    source TEXT,
    note TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_epistemic_entity ON epistemic_annotations(entity_id);
CREATE INDEX IF NOT EXISTS idx_epistemic_basis ON epistemic_annotations(basis);
CREATE INDEX IF NOT EXISTS idx_epistemic_certainty ON epistemic_annotations(certainty);
CREATE INDEX IF NOT EXISTS idx_epistemic_timestamp ON epistemic_annotations(timestamp);
"""


class EpistemicStore:
    """
    SQLite storage layer for epistemic annotations.
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the epistemic store.

        Args:
            db_path: Path to SQLite database (defaults to configured path)
        """
        if db_path is None:
            db_path = get_db_path("epistemic.db")
        self.db = DatabaseManager(db_path)
        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize database schema."""
        try:
            self.db.execute_script(EPISTEMIC_SCHEMA)
            logger.info("Epistemic database schema initialized")
        except Exception as e:
            logger.error(f"Failed to initialize schema: {e}")
            raise DatabaseError("Failed to initialize database schema", str(e))

    def _row_to_annotation(self, row: dict) -> EpistemicAnnotation:
        """Convert database row to EpistemicAnnotation model."""
        return EpistemicAnnotation(
            id=row["id"],
            entity_id=row["entity_id"],
            certainty=row["certainty"],
            basis=EpistemicBasis(row["basis"]),
            source=row.get("source"),
            note=row.get("note"),
            timestamp=datetime.fromisoformat(row["timestamp"]) if isinstance(row["timestamp"], str) else row["timestamp"],
        )

    def create(self, annotation_data: EpistemicAnnotationCreate) -> EpistemicAnnotation:
        """
        Create a new epistemic annotation.

        Args:
            annotation_data: Annotation creation data

        Returns:
            Created EpistemicAnnotation entity
        """
        annotation_id = str(uuid.uuid4())
        now = datetime.utcnow()

        query = """
            INSERT INTO epistemic_annotations (id, entity_id, certainty, basis, source, note, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            annotation_id,
            annotation_data.entity_id,
            annotation_data.certainty,
            annotation_data.basis.value,
            annotation_data.source,
            annotation_data.note,
            now.isoformat(),
        )

        self.db.execute_write(query, params)
        logger.info(f"Created epistemic annotation: {annotation_id}")

        return self.get_by_id(annotation_id)

    def get_by_id(self, annotation_id: str) -> EpistemicAnnotation:
        """
        Get an annotation by ID.

        Args:
            annotation_id: Annotation ID

        Returns:
            EpistemicAnnotation entity

        Raises:
            NotFoundError: If annotation not found
        """
        query = "SELECT * FROM epistemic_annotations WHERE id = ?"
        row = self.db.execute_one(query, (annotation_id,))

        if not row:
            raise NotFoundError("EpistemicAnnotation", annotation_id)

        return self._row_to_annotation(row)

    def get_all(
        self,
        offset: int = 0,
        limit: int = 50,
        basis: Optional[EpistemicBasis] = None,
    ) -> tuple[list[EpistemicAnnotation], int]:
        """
        Get all annotations with pagination.

        Args:
            offset: Number of items to skip
            limit: Maximum items to return
            basis: Optional filter by basis

        Returns:
            Tuple of (annotations list, total count)
        """
        where_clause = ""
        params = []

        if basis:
            where_clause = "WHERE basis = ?"
            params.append(basis.value)

        # Get total count
        count_query = f"SELECT COUNT(*) as count FROM epistemic_annotations {where_clause}"
        count_result = self.db.execute_one(count_query, tuple(params) if params else None)
        total = count_result["count"] if count_result else 0

        # Get paginated results
        query = f"""
            SELECT * FROM epistemic_annotations {where_clause}
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        rows = self.db.execute(query, tuple(params))

        annotations = [self._row_to_annotation(row) for row in rows]
        return annotations, total

    def update(self, annotation_id: str, update_data: EpistemicAnnotationUpdate) -> EpistemicAnnotation:
        """
        Update an epistemic annotation.

        Args:
            annotation_id: Annotation ID
            update_data: Update data

        Returns:
            Updated EpistemicAnnotation entity

        Raises:
            NotFoundError: If annotation not found
        """
        existing = self.get_by_id(annotation_id)

        updates = []
        params = []

        if update_data.entity_id is not None:
            updates.append("entity_id = ?")
            params.append(update_data.entity_id)
        if update_data.certainty is not None:
            updates.append("certainty = ?")
            params.append(update_data.certainty)
        if update_data.basis is not None:
            updates.append("basis = ?")
            params.append(update_data.basis.value)
        if update_data.source is not None:
            updates.append("source = ?")
            params.append(update_data.source)
        if update_data.note is not None:
            updates.append("note = ?")
            params.append(update_data.note)

        if not updates:
            return existing

        params.append(annotation_id)

        query = f"UPDATE epistemic_annotations SET {', '.join(updates)} WHERE id = ?"
        self.db.execute_write(query, tuple(params))

        logger.info(f"Updated epistemic annotation: {annotation_id}")
        return self.get_by_id(annotation_id)

    def delete(self, annotation_id: str) -> bool:
        """
        Delete an epistemic annotation.

        Args:
            annotation_id: Annotation ID

        Returns:
            True if deleted

        Raises:
            NotFoundError: If annotation not found
        """
        self.get_by_id(annotation_id)

        query = "DELETE FROM epistemic_annotations WHERE id = ?"
        self.db.execute_write(query, (annotation_id,))

        logger.info(f"Deleted epistemic annotation: {annotation_id}")
        return True

    def get_summary(self) -> EpistemicSummary:
        """
        Get summary statistics for epistemic annotations.

        Returns:
            EpistemicSummary with statistics
        """
        # Get total count
        count_query = "SELECT COUNT(*) as count FROM epistemic_annotations"
        count_result = self.db.execute_one(count_query)
        total = count_result["count"] if count_result else 0

        # Get counts by basis
        basis_query = """
            SELECT basis, COUNT(*) as count
            FROM epistemic_annotations
            GROUP BY basis
        """
        basis_rows = self.db.execute(basis_query)
        by_basis = {row["basis"]: row["count"] for row in basis_rows}

        # Ensure all basis types are represented
        for ebasis in EpistemicBasis:
            if ebasis.value not in by_basis:
                by_basis[ebasis.value] = 0

        # Get average certainty
        avg_query = "SELECT AVG(certainty) as avg_cert FROM epistemic_annotations"
        avg_result = self.db.execute_one(avg_query)
        avg_certainty = avg_result["avg_cert"] if avg_result and avg_result["avg_cert"] else 0.0

        # Get certainty distribution (bucketed)
        dist_query = """
            SELECT
                CASE
                    WHEN certainty < 0.2 THEN '0.0-0.2'
                    WHEN certainty < 0.4 THEN '0.2-0.4'
                    WHEN certainty < 0.6 THEN '0.4-0.6'
                    WHEN certainty < 0.8 THEN '0.6-0.8'
                    ELSE '0.8-1.0'
                END as bucket,
                COUNT(*) as count
            FROM epistemic_annotations
            GROUP BY bucket
        """
        dist_rows = self.db.execute(dist_query)
        certainty_distribution = {row["bucket"]: row["count"] for row in dist_rows}

        # Ensure all buckets are represented
        for bucket in ["0.0-0.2", "0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8-1.0"]:
            if bucket not in certainty_distribution:
                certainty_distribution[bucket] = 0

        return EpistemicSummary(
            total_count=total,
            by_basis=by_basis,
            avg_certainty=round(avg_certainty, 4),
            certainty_distribution=certainty_distribution,
        )

    def get_by_entity(
        self,
        entity_id: str,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[EpistemicAnnotation], int]:
        """
        Get annotations for a specific entity.

        Args:
            entity_id: Entity ID
            offset: Number of items to skip
            limit: Maximum items to return

        Returns:
            Tuple of (annotations list, total count)
        """
        where_clause = "WHERE entity_id = ?"
        params = [entity_id]

        # Get total count
        count_query = f"SELECT COUNT(*) as count FROM epistemic_annotations {where_clause}"
        count_result = self.db.execute_one(count_query, tuple(params))
        total = count_result["count"] if count_result else 0

        # Get paginated results
        query = f"""
            SELECT * FROM epistemic_annotations {where_clause}
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        rows = self.db.execute(query, tuple(params))

        annotations = [self._row_to_annotation(row) for row in rows]
        return annotations, total
