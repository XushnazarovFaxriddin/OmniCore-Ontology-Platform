"""
SQLite storage layer for the MMO Service.
"""

import uuid
from datetime import datetime
from typing import Optional

from common.database import DatabaseManager, get_db_path, json_serialize, json_deserialize
from common.logging_config import get_logger
from common.exceptions import NotFoundError, DatabaseError

from .models import MMOClass, MMOClassCreate, MMOClassUpdate, MMOSlot, MMOSlotCreate, MMOMetrics

logger = get_logger(__name__)

# Database schema
MMO_SCHEMA = """
CREATE TABLE IF NOT EXISTS mmo_classes (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    parent_class_id TEXT REFERENCES mmo_classes(id),
    properties TEXT,
    constraints TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mmo_slots (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    domain_class_id TEXT NOT NULL REFERENCES mmo_classes(id),
    range_type TEXT NOT NULL,
    cardinality TEXT DEFAULT '0..*',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mmo_metrics (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    completeness REAL DEFAULT 0.0,
    coverage REAL DEFAULT 0.0,
    coherence REAL DEFAULT 0.0,
    utility REAL DEFAULT 0.0,
    inclusivity REAL DEFAULT 0.0,
    mmo_score REAL DEFAULT 0.0,
    weights TEXT,
    predictive_power TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_mmo_slots_domain ON mmo_slots(domain_class_id);
CREATE INDEX IF NOT EXISTS idx_mmo_classes_parent ON mmo_classes(parent_class_id);

-- Initialize metrics row if not exists
INSERT OR IGNORE INTO mmo_metrics (id, completeness, coverage, coherence, utility, inclusivity, mmo_score, weights, predictive_power, last_updated)
VALUES (1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, NULL, NULL, CURRENT_TIMESTAMP);
"""


class MMOStore:
    """
    SQLite storage layer for MMO classes, slots, and metrics.
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the MMO store.

        Args:
            db_path: Path to SQLite database (defaults to configured path)
        """
        if db_path is None:
            db_path = get_db_path("mmo.db")
        self.db = DatabaseManager(db_path)
        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize database schema."""
        try:
            self.db.execute_script(MMO_SCHEMA)
            logger.info("MMO database schema initialized")
        except Exception as e:
            logger.error(f"Failed to initialize schema: {e}")
            raise DatabaseError("Failed to initialize database schema", str(e))

    def _row_to_class(self, row: dict) -> MMOClass:
        """Convert database row to MMOClass model."""
        return MMOClass(
            id=row["id"],
            name=row["name"],
            description=row.get("description"),
            parent_class_id=row.get("parent_class_id"),
            properties=json_deserialize(row.get("properties")) or [],
            constraints=json_deserialize(row.get("constraints")),
            created_at=datetime.fromisoformat(row["created_at"]) if isinstance(row["created_at"], str) else row["created_at"],
        )

    def _row_to_slot(self, row: dict) -> MMOSlot:
        """Convert database row to MMOSlot model."""
        return MMOSlot(
            id=row["id"],
            name=row["name"],
            domain_class_id=row["domain_class_id"],
            range_type=row["range_type"],
            cardinality=row.get("cardinality", "0..*"),
            description=row.get("description"),
            created_at=datetime.fromisoformat(row["created_at"]) if isinstance(row["created_at"], str) else row["created_at"],
        )

    # ==================== Class Operations ====================

    def create_class(self, class_data: MMOClassCreate) -> MMOClass:
        """
        Create a new MMO class.

        Args:
            class_data: Class creation data

        Returns:
            Created MMOClass entity
        """
        class_id = str(uuid.uuid4())
        now = datetime.utcnow()

        query = """
            INSERT INTO mmo_classes (id, name, description, parent_class_id, properties, constraints, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            class_id,
            class_data.name,
            class_data.description,
            class_data.parent_class_id,
            json_serialize(class_data.properties),
            json_serialize(class_data.constraints),
            now.isoformat(),
        )

        self.db.execute_write(query, params)
        logger.info(f"Created MMO class: {class_id}")

        return self.get_class_by_id(class_id)

    def get_class_by_id(self, class_id: str) -> MMOClass:
        """
        Get an MMO class by ID.

        Args:
            class_id: Class ID

        Returns:
            MMOClass entity

        Raises:
            NotFoundError: If class not found
        """
        query = "SELECT * FROM mmo_classes WHERE id = ?"
        row = self.db.execute_one(query, (class_id,))

        if not row:
            raise NotFoundError("MMOClass", class_id)

        return self._row_to_class(row)

    def get_all_classes(self, offset: int = 0, limit: int = 100) -> tuple[list[MMOClass], int]:
        """
        Get all MMO classes with pagination.

        Args:
            offset: Number of items to skip
            limit: Maximum items to return

        Returns:
            Tuple of (classes list, total count)
        """
        count_query = "SELECT COUNT(*) as count FROM mmo_classes"
        count_result = self.db.execute_one(count_query)
        total = count_result["count"] if count_result else 0

        query = """
            SELECT * FROM mmo_classes
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        rows = self.db.execute(query, (limit, offset))

        classes = [self._row_to_class(row) for row in rows]
        return classes, total

    def update_class(self, class_id: str, update_data: MMOClassUpdate) -> MMOClass:
        """
        Update an MMO class.

        Args:
            class_id: Class ID
            update_data: Update data

        Returns:
            Updated MMOClass entity
        """
        existing = self.get_class_by_id(class_id)

        updates = []
        params = []

        if update_data.name is not None:
            updates.append("name = ?")
            params.append(update_data.name)
        if update_data.description is not None:
            updates.append("description = ?")
            params.append(update_data.description)
        if update_data.parent_class_id is not None:
            updates.append("parent_class_id = ?")
            params.append(update_data.parent_class_id)
        if update_data.properties is not None:
            updates.append("properties = ?")
            params.append(json_serialize(update_data.properties))
        if update_data.constraints is not None:
            updates.append("constraints = ?")
            params.append(json_serialize(update_data.constraints))

        if not updates:
            return existing

        params.append(class_id)

        query = f"UPDATE mmo_classes SET {', '.join(updates)} WHERE id = ?"
        self.db.execute_write(query, tuple(params))

        logger.info(f"Updated MMO class: {class_id}")
        return self.get_class_by_id(class_id)

    def delete_class(self, class_id: str) -> bool:
        """
        Delete an MMO class.

        Args:
            class_id: Class ID

        Returns:
            True if deleted
        """
        self.get_class_by_id(class_id)

        # Delete associated slots first
        self.db.execute_write("DELETE FROM mmo_slots WHERE domain_class_id = ?", (class_id,))

        # Delete the class
        self.db.execute_write("DELETE FROM mmo_classes WHERE id = ?", (class_id,))

        logger.info(f"Deleted MMO class: {class_id}")
        return True

    # ==================== Slot Operations ====================

    def create_slot(self, slot_data: MMOSlotCreate) -> MMOSlot:
        """
        Create a new MMO slot.

        Args:
            slot_data: Slot creation data

        Returns:
            Created MMOSlot entity
        """
        # Verify domain class exists
        self.get_class_by_id(slot_data.domain_class_id)

        slot_id = str(uuid.uuid4())
        now = datetime.utcnow()

        query = """
            INSERT INTO mmo_slots (id, name, domain_class_id, range_type, cardinality, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            slot_id,
            slot_data.name,
            slot_data.domain_class_id,
            slot_data.range_type,
            slot_data.cardinality,
            slot_data.description,
            now.isoformat(),
        )

        self.db.execute_write(query, params)
        logger.info(f"Created MMO slot: {slot_id}")

        return self.get_slot_by_id(slot_id)

    def get_slot_by_id(self, slot_id: str) -> MMOSlot:
        """
        Get an MMO slot by ID.

        Args:
            slot_id: Slot ID

        Returns:
            MMOSlot entity
        """
        query = "SELECT * FROM mmo_slots WHERE id = ?"
        row = self.db.execute_one(query, (slot_id,))

        if not row:
            raise NotFoundError("MMOSlot", slot_id)

        return self._row_to_slot(row)

    def get_all_slots(self, offset: int = 0, limit: int = 100) -> tuple[list[MMOSlot], int]:
        """
        Get all MMO slots with pagination.

        Args:
            offset: Number of items to skip
            limit: Maximum items to return

        Returns:
            Tuple of (slots list, total count)
        """
        count_query = "SELECT COUNT(*) as count FROM mmo_slots"
        count_result = self.db.execute_one(count_query)
        total = count_result["count"] if count_result else 0

        query = """
            SELECT * FROM mmo_slots
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        rows = self.db.execute(query, (limit, offset))

        slots = [self._row_to_slot(row) for row in rows]
        return slots, total

    def delete_slot(self, slot_id: str) -> bool:
        """
        Delete an MMO slot.

        Args:
            slot_id: Slot ID

        Returns:
            True if deleted
        """
        self.get_slot_by_id(slot_id)

        self.db.execute_write("DELETE FROM mmo_slots WHERE id = ?", (slot_id,))

        logger.info(f"Deleted MMO slot: {slot_id}")
        return True

    # ==================== Metrics Operations ====================

    def get_metrics(self) -> MMOMetrics:
        """
        Get current MMO metrics.

        Returns:
            MMOMetrics entity
        """
        query = "SELECT * FROM mmo_metrics WHERE id = 1"
        row = self.db.execute_one(query)

        if not row:
            # Initialize metrics if not exists
            return MMOMetrics()

        # Prepare kwargs to allow Pydantic defaults for missing/null content
        metrics_data = {
            "completeness": row["completeness"],
            "coverage": row["coverage"],
            "coherence": row["coherence"],
            "utility": row["utility"],
            "inclusivity": row["inclusivity"],
            "mmo_score": row["mmo_score"],
            "last_updated": datetime.fromisoformat(row["last_updated"]) if isinstance(row["last_updated"], str) else row["last_updated"],
        }
        
        weights = json_deserialize(row.get("weights"))
        if weights is not None:
            metrics_data["weights"] = weights
            
        predictive_power = json_deserialize(row.get("predictive_power"))
        if predictive_power is not None:
            metrics_data["predictive_power"] = predictive_power

        return MMOMetrics(**metrics_data)

    def update_metrics(self, metrics: MMOMetrics) -> MMOMetrics:
        """
        Update MMO metrics.

        Args:
            metrics: New metrics values

        Returns:
            Updated MMOMetrics entity
        """
        now = datetime.utcnow()

        query = """
            UPDATE mmo_metrics
            SET completeness = ?, coverage = ?, coherence = ?, utility = ?, inclusivity = ?, mmo_score = ?, weights = ?, predictive_power = ?, last_updated = ?
            WHERE id = 1
        """
        params = (
            metrics.completeness,
            metrics.coverage,
            metrics.coherence,
            metrics.utility,
            metrics.inclusivity,
            metrics.mmo_score,
            json_serialize(metrics.weights),
            json_serialize(metrics.predictive_power),
            now.isoformat(),
        )

        self.db.execute_write(query, params)
        logger.info("Updated MMO metrics")

        return self.get_metrics()



    def calculate_metrics(self) -> MMOMetrics:
        """
        Calculate MMO metrics based on current data.

        v10 Spec: Self-Calibrating Metrics
        Formula: MMO_Score = w₁·C + w₂·Cv + w₃·Ch + w₄·U + w₅·I
        where wᵢ = softmax(predictive_powerᵢ)
        """
        import math
        
        # Get counts
        class_count = self.db.execute_one("SELECT COUNT(*) as count FROM mmo_classes")["count"]
        slot_count = self.db.execute_one("SELECT COUNT(*) as count FROM mmo_slots")["count"]

        # Calculate basic metrics (simplified but v10 compliant structure)
        # Completeness: Based on having classes and slots defined
        completeness = min(1.0, (class_count / 10) * 0.5 + (slot_count / 20) * 0.5) if class_count > 0 else 0.0

        # Coverage: Based on slot coverage of classes
        coverage = min(1.0, slot_count / max(class_count, 1) / 3) if class_count > 0 else 0.0

        # Coherence: Check for orphan slots or circular references (simplified)
        coherence = 0.95 if class_count > 0 and slot_count > 0 else 0.5

        # Utility: Based on structural completeness (Simulated query latency impact)
        # U = 1 - (avg_query_latency_ms / 1000)
        # Assuming nominal latency for now
        utility = (completeness + coverage) / 2

        # Inclusivity: Bias vectors (Placeholder)
        inclusivity = 0.7 if class_count > 0 else 0.0

        # Get current predictive power (simulated self-calibration)
        current_metrics = self.get_metrics()
        predictive_power = current_metrics.predictive_power
        
        # Calculate Softmax Weights
        # w_i = exp(p_i) / sum(exp(p_j))
        exp_values = {k: math.exp(v) for k, v in predictive_power.items()}
        total_exp = sum(exp_values.values())
        weights = {k: v / total_exp for k, v in exp_values.items()}

        # Calculate weighted MMO score
        mmo_score = (
            completeness * weights["completeness"] +
            coverage * weights["coverage"] +
            coherence * weights["coherence"] +
            utility * weights["utility"] +
            inclusivity * weights["inclusivity"]
        )

        metrics = MMOMetrics(
            completeness=round(completeness, 4),
            coverage=round(coverage, 4),
            coherence=round(coherence, 4),
            utility=round(utility, 4),
            inclusivity=round(inclusivity, 4),
            mmo_score=round(mmo_score, 4),
            weights=weights,
            predictive_power=predictive_power,
            last_updated=datetime.utcnow(),
        )

        return self.update_metrics(metrics)

    def get_counts(self) -> dict:
        """Get counts of classes and slots."""
        class_count = self.db.execute_one("SELECT COUNT(*) as count FROM mmo_classes")["count"]
        slot_count = self.db.execute_one("SELECT COUNT(*) as count FROM mmo_slots")["count"]
        return {"classes": class_count, "slots": slot_count}
