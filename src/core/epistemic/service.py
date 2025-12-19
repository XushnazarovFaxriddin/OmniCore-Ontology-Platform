"""
Business logic for the Epistemic Service.
"""

from typing import Optional

from common.logging_config import get_logger
from common.models import PaginatedResponse

from .store import EpistemicStore
from .models import EpistemicAnnotation, EpistemicAnnotationCreate, EpistemicAnnotationUpdate, EpistemicBasis, EpistemicSummary

logger = get_logger(__name__)


class EpistemicService:
    """
    Business logic layer for epistemic annotations.
    """

    def __init__(self, store: Optional[EpistemicStore] = None):
        """
        Initialize the epistemic service.

        Args:
            store: Optional custom store instance
        """
        self.store = store or EpistemicStore()

    def create_annotation(self, annotation_data: EpistemicAnnotationCreate) -> EpistemicAnnotation:
        """
        Create a new epistemic annotation.

        Args:
            annotation_data: Annotation creation data

        Returns:
            Created EpistemicAnnotation entity
        """
        logger.info(
            f"Creating epistemic annotation for entity {annotation_data.entity_id} ({annotation_data.basis})"
        )
        return self.store.create(annotation_data)

    def get_annotation(self, annotation_id: str) -> EpistemicAnnotation:
        """
        Get an annotation by ID.

        Args:
            annotation_id: Annotation ID

        Returns:
            EpistemicAnnotation entity
        """
        return self.store.get_by_id(annotation_id)

    def list_annotations(
        self,
        offset: int = 0,
        limit: int = 50,
        basis: Optional[EpistemicBasis] = None,
    ) -> PaginatedResponse:
        """
        List annotations with pagination.

        Args:
            offset: Number of items to skip
            limit: Maximum items to return
            basis: Optional filter by basis

        Returns:
            Paginated response with annotations
        """
        annotations, total = self.store.get_all(
            offset=offset,
            limit=limit,
            basis=basis,
        )

        return PaginatedResponse(
            items=annotations,
            total=total,
            offset=offset,
            limit=limit,
            has_more=(offset + len(annotations)) < total,
        )

    def update_annotation(self, annotation_id: str, update_data: EpistemicAnnotationUpdate) -> EpistemicAnnotation:
        """
        Update an epistemic annotation.

        Args:
            annotation_id: Annotation ID
            update_data: Update data

        Returns:
            Updated EpistemicAnnotation entity
        """
        logger.info(f"Updating epistemic annotation: {annotation_id}")
        return self.store.update(annotation_id, update_data)

    def delete_annotation(self, annotation_id: str) -> bool:
        """
        Delete an epistemic annotation.

        Args:
            annotation_id: Annotation ID

        Returns:
            True if deleted
        """
        logger.info(f"Deleting epistemic annotation: {annotation_id}")
        return self.store.delete(annotation_id)

    def get_summary(self) -> EpistemicSummary:
        """
        Get summary statistics.

        Returns:
            EpistemicSummary with statistics
        """
        return self.store.get_summary()

    def get_annotations_by_basis(
        self,
        basis: EpistemicBasis,
        offset: int = 0,
        limit: int = 50,
    ) -> PaginatedResponse:
        """
        Get annotations filtered by basis.

        Args:
            basis: Epistemic basis to filter by
            offset: Number of items to skip
            limit: Maximum items to return

        Returns:
            Paginated response with annotations
        """
        annotations, total = self.store.get_all(
            offset=offset,
            limit=limit,
            basis=basis,
        )

        return PaginatedResponse(
            items=annotations,
            total=total,
            offset=offset,
            limit=limit,
            has_more=(offset + len(annotations)) < total,
        )

    def get_annotations_for_entity(
        self,
        entity_id: str,
        offset: int = 0,
        limit: int = 50,
    ) -> PaginatedResponse:
        """
        Get annotations for a specific entity.

        Args:
            entity_id: Entity ID
            offset: Number of items to skip
            limit: Maximum items to return

        Returns:
            Paginated response with annotations
        """
        annotations, total = self.store.get_by_entity(
            entity_id=entity_id,
            offset=offset,
            limit=limit,
        )

        return PaginatedResponse(
            items=annotations,
            total=total,
            offset=offset,
            limit=limit,
            has_more=(offset + len(annotations)) < total,
        )
