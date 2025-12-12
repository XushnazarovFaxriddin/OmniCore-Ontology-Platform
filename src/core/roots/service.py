"""
Business logic for the Roots Service.
"""

from typing import Optional

from common.logging_config import get_logger
from common.models import PaginatedResponse

from .store import RootsStore
from .models import Root, RootCreate, RootUpdate, RootType, RootSummary

logger = get_logger(__name__)


class RootsService:
    """
    Business logic layer for root entities.
    """

    def __init__(self, store: Optional[RootsStore] = None):
        """
        Initialize the roots service.

        Args:
            store: Optional custom store instance
        """
        self.store = store or RootsStore()

    def create_root(self, root_data: RootCreate) -> Root:
        """
        Create a new root entity.

        Args:
            root_data: Root creation data

        Returns:
            Created Root entity
        """
        logger.info(f"Creating root: {root_data.name} ({root_data.root_type})")
        return self.store.create(root_data)

    def get_root(self, root_id: str) -> Root:
        """
        Get a root by ID.

        Args:
            root_id: Root ID

        Returns:
            Root entity
        """
        return self.store.get_by_id(root_id)

    def list_roots(
        self,
        offset: int = 0,
        limit: int = 50,
        root_type: Optional[RootType] = None,
    ) -> PaginatedResponse:
        """
        List roots with pagination.

        Args:
            offset: Number of items to skip
            limit: Maximum items to return
            root_type: Optional filter by root type

        Returns:
            Paginated response with roots
        """
        roots, total = self.store.get_all(
            offset=offset,
            limit=limit,
            root_type=root_type,
        )

        return PaginatedResponse(
            items=roots,
            total=total,
            offset=offset,
            limit=limit,
            has_more=(offset + len(roots)) < total,
        )

    def update_root(self, root_id: str, update_data: RootUpdate) -> Root:
        """
        Update a root entity.

        Args:
            root_id: Root ID
            update_data: Update data

        Returns:
            Updated Root entity
        """
        logger.info(f"Updating root: {root_id}")
        return self.store.update(root_id, update_data)

    def delete_root(self, root_id: str) -> bool:
        """
        Delete a root entity.

        Args:
            root_id: Root ID

        Returns:
            True if deleted
        """
        logger.info(f"Deleting root: {root_id}")
        return self.store.delete(root_id)

    def get_summary(self) -> RootSummary:
        """
        Get summary statistics.

        Returns:
            RootSummary with statistics
        """
        return self.store.get_summary()

    def get_roots_by_type(
        self,
        root_type: RootType,
        offset: int = 0,
        limit: int = 50,
    ) -> PaginatedResponse:
        """
        Get roots filtered by type.

        Args:
            root_type: Root type to filter by
            offset: Number of items to skip
            limit: Maximum items to return

        Returns:
            Paginated response with roots
        """
        roots, total = self.store.get_by_type(
            root_type=root_type,
            offset=offset,
            limit=limit,
        )

        return PaginatedResponse(
            items=roots,
            total=total,
            offset=offset,
            limit=limit,
            has_more=(offset + len(roots)) < total,
        )
