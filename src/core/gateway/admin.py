
"""
Admin routes for database management and system operations.
"""
import os
import glob
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from common.config import settings
from common.logging_config import get_logger
from common.database import get_db_path

# Import Stores/Services for seeding if available
# Since we are in the gateway, we might share code with services if they are in the same repo.
# We will use direct DB access for reset, and service proxies or direct store usage for seeding.
from core.mmo.store import MMOStore, MMOClassCreate, MMOSlotCreate
# Note: For other services, we might need similar imports or make HTTP calls.
# For MVP/Dev, we'll focus on MMO seeding as a proof of concept and hard reset for everything.

logger = get_logger(__name__)

router = APIRouter(tags=["Admin"])

class AdminResponse(BaseModel):
    status: str
    message: str
    details: dict = {}

def delete_database_files():
    """Delete all SQLite database files in the configured directory."""
    try:
        # Check if path is directory
        db_path = settings.database_path
        if os.path.isdir(db_path):
            files = glob.glob(os.path.join(db_path, "*.db"))
            deleted = []
            for f in files:
                try:
                    os.remove(f)
                    deleted.append(os.path.basename(f))
                except Exception as e:
                    logger.error(f"Failed to delete {f}: {e}")
            return deleted
        else:
            # Fallback if specific file
            if os.path.exists(db_path) and db_path.endswith(".db"):
                os.remove(db_path)
                return [os.path.basename(db_path)]
    except Exception as e:
        logger.error(f"Error resetting databases: {e}")
        return []

def seed_mmo_data():
    """Seed the MMO database with initial data."""
    try:
        store = MMOStore()  # Will re-init schema if DB was deleted
        
        # Create Root Class
        entity = store.create_class(MMOClassCreate(
            name="Entity",
            description="The most fundamental concept in the ontology."
        ))
        
        # Create Subclasses
        physical = store.create_class(MMOClassCreate(
            name="PhysicalObject",
            description="An object that exists in the physical world.",
            parent_class_id=entity.id
        ))
        
        abstract = store.create_class(MMOClassCreate(
            name="AbstractConcept",
            description="A concept that exists only in the mind or theory.",
            parent_class_id=entity.id
        ))

        # Create Slots
        store.create_slot(MMOSlotCreate(
            name="hasName",
            domain_class_id=entity.id,
            range_type="string",
            cardinality="1..1",
            description="The name of the entity."
        ))

        store.create_slot(MMOSlotCreate(
            name="hasMass",
            domain_class_id=physical.id,
            range_type="float",
            cardinality="0..1",
            description="The mass of the object in kg."
        ))

        # Calculate initial metrics
        store.calculate_metrics()
        
        logger.info("MMO Database seeded successfully")
        return {"classes": 3, "slots": 2}
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        raise

@router.post("/admin/database/reset", response_model=AdminResponse)
async def reset_database():
    """
    Reset the system databases.
    WARNING: This deletes all data!
    """
    if settings.omnicore_env.lower() == "production":
        raise HTTPException(status_code=403, detail="Reset not allowed in production")

    deleted_files = delete_database_files()
    
    return AdminResponse(
        status="success",
        message="Databases reset successfully",
        details={"deleted_files": deleted_files}
    )

@router.post("/admin/database/seed", response_model=AdminResponse)
async def seed_database(background_tasks: BackgroundTasks):
    """
    Seed the system with sample data.
    """
    try:
        # We can run this in background if it's heavy
        stats = seed_mmo_data()
        return AdminResponse(
            status="success", 
            message="Database seeding completed",
            details=stats
        )
    except Exception as e:
        logger.error(f"Seeding error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
