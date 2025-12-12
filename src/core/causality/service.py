"""
Business logic for the Causality Service.
"""

from typing import Optional

from common.logging_config import get_logger
from common.models import PaginatedResponse

from .store import CausalityStore
from .models import CausalityLink, CausalityLinkCreate, CausalityLinkUpdate, CausalityType, CausalitySummary

logger = get_logger(__name__)


class CausalityService:
    """
    Business logic layer for causality links.
    """

    def __init__(self, store: Optional[CausalityStore] = None):
        """
        Initialize the causality service.

        Args:
            store: Optional custom store instance
        """
        self.store = store or CausalityStore()

    def create_link(self, link_data: CausalityLinkCreate) -> CausalityLink:
        """
        Create a new causality link.

        Args:
            link_data: Link creation data

        Returns:
            Created CausalityLink entity
        """
        logger.info(
            f"Creating causality link: {link_data.source_entity_id} -> {link_data.target_entity_id} ({link_data.causality_type})"
        )
        return self.store.create(link_data)

    def get_link(self, link_id: str) -> CausalityLink:
        """
        Get a causality link by ID.

        Args:
            link_id: Link ID

        Returns:
            CausalityLink entity
        """
        return self.store.get_by_id(link_id)

    def list_links(
        self,
        offset: int = 0,
        limit: int = 50,
        causality_type: Optional[CausalityType] = None,
    ) -> PaginatedResponse:
        """
        List causality links with pagination.

        Args:
            offset: Number of items to skip
            limit: Maximum items to return
            causality_type: Optional filter by type

        Returns:
            Paginated response with links
        """
        links, total = self.store.get_all(
            offset=offset,
            limit=limit,
            causality_type=causality_type,
        )

        return PaginatedResponse(
            items=links,
            total=total,
            offset=offset,
            limit=limit,
            has_more=(offset + len(links)) < total,
        )

    def update_link(self, link_id: str, update_data: CausalityLinkUpdate) -> CausalityLink:
        """
        Update a causality link.

        Args:
            link_id: Link ID
            update_data: Update data

        Returns:
            Updated CausalityLink entity
        """
        logger.info(f"Updating causality link: {link_id}")
        return self.store.update(link_id, update_data)

    def delete_link(self, link_id: str) -> bool:
        """
        Delete a causality link.

        Args:
            link_id: Link ID

        Returns:
            True if deleted
        """
        logger.info(f"Deleting causality link: {link_id}")
        return self.store.delete(link_id)

    def get_summary(self) -> CausalitySummary:
        """
        Get summary statistics.

        Returns:
            CausalitySummary with statistics
        """
        return self.store.get_summary()

    def get_links_by_type(
        self,
        causality_type: CausalityType,
        offset: int = 0,
        limit: int = 50,
    ) -> PaginatedResponse:
        """
        Get causality links filtered by type.

        Args:
            causality_type: Causality type to filter by
            offset: Number of items to skip
            limit: Maximum items to return

        Returns:
            Paginated response with links
        """
        links, total = self.store.get_all(
            offset=offset,
            limit=limit,
            causality_type=causality_type,
        )

        return PaginatedResponse(
            items=links,
            total=total,
            offset=offset,
            limit=limit,
            has_more=(offset + len(links)) < total,
        )

    def get_links_by_entity(
        self,
        entity_id: str,
        offset: int = 0,
        limit: int = 50,
    ) -> PaginatedResponse:
        """
        Get causality links involving a specific entity.

        Args:
            entity_id: Entity ID
            offset: Number of items to skip
            limit: Maximum items to return

        Returns:
            Paginated response with links
        """
        links, total = self.store.get_by_entity(
            entity_id=entity_id,
            offset=offset,
            limit=limit,
        )

        return PaginatedResponse(
            items=links,
            total=total,
            offset=offset,
            limit=limit,
            has_more=(offset + len(links)) < total,
        )
