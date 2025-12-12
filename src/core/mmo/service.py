"""
Business logic for the MMO Service.
"""

from typing import Optional

from common.logging_config import get_logger
from common.models import PaginatedResponse

from .store import MMOStore
from .models import MMOClass, MMOClassCreate, MMOClassUpdate, MMOSlot, MMOSlotCreate, MMOMetrics, MMOSchema

logger = get_logger(__name__)


class MMOService:
    """
    Business logic layer for MMO (Meta-Meta-Ontology).
    """

    def __init__(self, store: Optional[MMOStore] = None):
        """
        Initialize the MMO service.

        Args:
            store: Optional custom store instance
        """
        self.store = store or MMOStore()

    # ==================== Class Operations ====================

    def create_class(self, class_data: MMOClassCreate) -> MMOClass:
        """
        Create a new MMO class.

        Args:
            class_data: Class creation data

        Returns:
            Created MMOClass entity
        """
        logger.info(f"Creating MMO class: {class_data.name}")
        return self.store.create_class(class_data)

    def get_class(self, class_id: str) -> MMOClass:
        """
        Get an MMO class by ID.

        Args:
            class_id: Class ID

        Returns:
            MMOClass entity
        """
        return self.store.get_class_by_id(class_id)

    def list_classes(self, offset: int = 0, limit: int = 100) -> PaginatedResponse:
        """
        List MMO classes with pagination.

        Args:
            offset: Number of items to skip
            limit: Maximum items to return

        Returns:
            Paginated response with classes
        """
        classes, total = self.store.get_all_classes(offset=offset, limit=limit)

        return PaginatedResponse(
            items=classes,
            total=total,
            offset=offset,
            limit=limit,
            has_more=(offset + len(classes)) < total,
        )

    def update_class(self, class_id: str, update_data: MMOClassUpdate) -> MMOClass:
        """
        Update an MMO class.

        Args:
            class_id: Class ID
            update_data: Update data

        Returns:
            Updated MMOClass entity
        """
        logger.info(f"Updating MMO class: {class_id}")
        return self.store.update_class(class_id, update_data)

    def delete_class(self, class_id: str) -> bool:
        """
        Delete an MMO class.

        Args:
            class_id: Class ID

        Returns:
            True if deleted
        """
        logger.info(f"Deleting MMO class: {class_id}")
        return self.store.delete_class(class_id)

    # ==================== Slot Operations ====================

    def create_slot(self, slot_data: MMOSlotCreate) -> MMOSlot:
        """
        Create a new MMO slot.

        Args:
            slot_data: Slot creation data

        Returns:
            Created MMOSlot entity
        """
        logger.info(f"Creating MMO slot: {slot_data.name}")
        return self.store.create_slot(slot_data)

    def get_slot(self, slot_id: str) -> MMOSlot:
        """
        Get an MMO slot by ID.

        Args:
            slot_id: Slot ID

        Returns:
            MMOSlot entity
        """
        return self.store.get_slot_by_id(slot_id)

    def list_slots(self, offset: int = 0, limit: int = 100) -> PaginatedResponse:
        """
        List MMO slots with pagination.

        Args:
            offset: Number of items to skip
            limit: Maximum items to return

        Returns:
            Paginated response with slots
        """
        slots, total = self.store.get_all_slots(offset=offset, limit=limit)

        return PaginatedResponse(
            items=slots,
            total=total,
            offset=offset,
            limit=limit,
            has_more=(offset + len(slots)) < total,
        )

    def delete_slot(self, slot_id: str) -> bool:
        """
        Delete an MMO slot.

        Args:
            slot_id: Slot ID

        Returns:
            True if deleted
        """
        logger.info(f"Deleting MMO slot: {slot_id}")
        return self.store.delete_slot(slot_id)

    # ==================== Metrics Operations ====================

    def get_metrics(self) -> MMOMetrics:
        """
        Get current MMO metrics.

        Returns:
            MMOMetrics entity
        """
        return self.store.get_metrics()

    def recalculate_metrics(self) -> MMOMetrics:
        """
        Recalculate MMO metrics based on current data.

        Returns:
            Updated MMOMetrics entity
        """
        logger.info("Recalculating MMO metrics")
        return self.store.calculate_metrics()

    # ==================== Schema Operations ====================

    def get_schema(self) -> MMOSchema:
        """
        Get full MMO schema including classes, slots, and metrics.

        Returns:
            MMOSchema with all components
        """
        classes, _ = self.store.get_all_classes(offset=0, limit=1000)
        slots, _ = self.store.get_all_slots(offset=0, limit=1000)
        metrics = self.store.get_metrics()

        return MMOSchema(
            classes=classes,
            slots=slots,
            metrics=metrics,
        )

    def get_counts(self) -> dict:
        """Get counts of classes and slots."""
        return self.store.get_counts()
