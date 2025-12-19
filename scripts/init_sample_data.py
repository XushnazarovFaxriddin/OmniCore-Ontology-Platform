#!/usr/bin/env python3
"""
OmniCore Platform v10 - Sample Data Initialization Script
Creates sample data for demonstration and testing purposes.
Run: python scripts/init_sample_data.py
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from datetime import datetime
import uuid

from common.database import DatabaseManager, get_db_path


def create_roots_data():
    """Create sample root entities"""
    db = DatabaseManager(get_db_path("roots.db"))

    # Ensure table exists
    db.execute_script("""
        CREATE TABLE IF NOT EXISTS roots (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            root_type TEXT NOT NULL CHECK(root_type IN ('EXTANT', 'ABSTRACT', 'MENTAL', 'FICTIVE')),
            description TEXT,
            source TEXT,
            confidence REAL DEFAULT 1.0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_roots_type ON roots(root_type);
        CREATE INDEX IF NOT EXISTS idx_roots_name ON roots(name);
    """)

    # Sample roots data
    roots = [
        # EXTANT - Physical, observable entities
        ("Mount Everest", "EXTANT", "Highest mountain on Earth, located in the Himalayas", "Geographic Database", 1.0),
        ("Atlantic Ocean", "EXTANT", "Second largest ocean on Earth", "Geographic Database", 1.0),
        ("DNA Molecule", "EXTANT", "Deoxyribonucleic acid - carrier of genetic information", "Biology Textbook", 1.0),
        ("Human Brain", "EXTANT", "Central organ of the human nervous system", "Medical Reference", 1.0),
        ("Solar System", "EXTANT", "Our planetary system including Sun and 8 planets", "Astronomy Reference", 1.0),
        ("Tiger", "EXTANT", "Largest living cat species (Panthera tigris)", "Zoology Reference", 1.0),
        ("Gold Atom", "EXTANT", "Chemical element with atomic number 79", "Periodic Table", 1.0),
        ("Amazon Rainforest", "EXTANT", "Largest tropical rainforest in the world", "Geographic Database", 1.0),

        # ABSTRACT - Non-physical concepts
        ("Mathematics", "ABSTRACT", "The abstract science of number, quantity, and space", "Academic Definition", 1.0),
        ("Justice", "ABSTRACT", "Moral rightness based on ethics, law, and equity", "Philosophy Reference", 0.85),
        ("Democracy", "ABSTRACT", "System of government by the whole population", "Political Science", 0.9),
        ("Algorithm", "ABSTRACT", "A step-by-step procedure for calculations", "Computer Science", 1.0),
        ("Consciousness", "ABSTRACT", "The state of being aware and responsive", "Philosophy/Neuroscience", 0.7),
        ("Entropy", "ABSTRACT", "Measure of disorder or randomness in a system", "Physics/Thermodynamics", 1.0),
        ("Grammar", "ABSTRACT", "The set of structural rules governing language", "Linguistics", 1.0),
        ("Economic Value", "ABSTRACT", "Worth of goods/services in exchange", "Economics", 0.85),

        # MENTAL - Mind-dependent entities
        ("Fear", "MENTAL", "An unpleasant emotion caused by perceived danger", "Psychology", 0.95),
        ("Dream", "MENTAL", "A series of images and sensations occurring during sleep", "Psychology", 0.9),
        ("Memory", "MENTAL", "The faculty by which the mind stores information", "Cognitive Science", 0.95),
        ("Imagination", "MENTAL", "The faculty of forming mental images", "Psychology", 0.85),
        ("Intuition", "MENTAL", "The ability to understand something instinctively", "Psychology", 0.75),
        ("Belief", "MENTAL", "Acceptance that something is true", "Philosophy/Psychology", 0.8),
        ("Perception", "MENTAL", "The ability to see, hear, or become aware", "Cognitive Science", 0.9),
        ("Emotion", "MENTAL", "A strong feeling derived from circumstances", "Psychology", 0.95),

        # FICTIVE - Fictional entities
        ("Sherlock Holmes", "FICTIVE", "Fictional detective created by Arthur Conan Doyle", "Literature", 1.0),
        ("Hogwarts", "FICTIVE", "Fictional school of witchcraft and wizardry", "Harry Potter Universe", 1.0),
        ("Middle-earth", "FICTIVE", "Fictional setting in Tolkien's works", "Tolkien Legendarium", 1.0),
        ("Unicorn", "FICTIVE", "Legendary creature depicted as a horse with a horn", "Mythology", 1.0),
        ("Excalibur", "FICTIVE", "Legendary sword of King Arthur", "Arthurian Legend", 1.0),
        ("Atlantis", "FICTIVE", "Legendary island civilization from Greek mythology", "Greek Mythology", 0.95),
        ("Starship Enterprise", "FICTIVE", "Fictional spacecraft from Star Trek", "Star Trek Universe", 1.0),
        ("Mordor", "FICTIVE", "Fictional land in Tolkien's Middle-earth", "Tolkien Legendarium", 1.0),
    ]

    now = datetime.utcnow().isoformat()
    for name, root_type, description, source, confidence in roots:
        root_id = str(uuid.uuid4())
        try:
            db.execute_write(
                """
                INSERT INTO roots (id, name, root_type, description, source, confidence, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (root_id, name, root_type, description, source, confidence, now, now)
            )
        except Exception as e:
            print(f"  Skipping '{name}' (may already exist): {e}")

    print(f"Created {len(roots)} sample root entities")


def create_causality_data():
    """Create sample causality links"""
    db = DatabaseManager(get_db_path("causality.db"))

    # Ensure table exists
    db.execute_script("""
        CREATE TABLE IF NOT EXISTS causality_links (
            id TEXT PRIMARY KEY,
            source_entity_id TEXT NOT NULL,
            target_entity_id TEXT NOT NULL,
            causality_type TEXT NOT NULL CHECK(causality_type IN ('EFFICIENT', 'FINAL', 'MATERIAL', 'FORMAL', 'EMERGENT')),
            description TEXT,
            confidence REAL DEFAULT 0.8,
            inferred_by TEXT DEFAULT 'manual',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_causality_source ON causality_links(source_entity_id);
        CREATE INDEX IF NOT EXISTS idx_causality_target ON causality_links(target_entity_id);
        CREATE INDEX IF NOT EXISTS idx_causality_type ON causality_links(causality_type);
    """)

    # Get root IDs
    roots_db = DatabaseManager(get_db_path("roots.db"))
    roots = roots_db.execute("SELECT id, name FROM roots")
    root_map = {r['name']: r['id'] for r in roots}

    # Sample causality links
    links = [
        # EFFICIENT cause - produces effect
        ("Human Brain", "Memory", "EFFICIENT", "Brain processes create and store memories", 0.95),
        ("Solar System", "Human Brain", "EFFICIENT", "Cosmic conditions enabled brain evolution", 0.7),
        ("DNA Molecule", "Tiger", "EFFICIENT", "DNA encodes genetic information for tiger development", 0.98),

        # FINAL cause - purpose/goal
        ("Algorithm", "Mathematics", "FINAL", "Algorithms serve mathematical computation purposes", 0.9),
        ("Democracy", "Justice", "FINAL", "Democracy aims to achieve justice", 0.75),
        ("Grammar", "Mathematics", "FORMAL", "Both follow formal structural rules", 0.65),

        # MATERIAL cause - what something is made of
        ("Gold Atom", "Mount Everest", "MATERIAL", "Gold atoms are part of Earth's crust including mountains", 0.6),
        ("DNA Molecule", "Human Brain", "MATERIAL", "DNA provides the material blueprint for brain development", 0.95),

        # FORMAL cause - shape/pattern
        ("Mathematics", "Algorithm", "FORMAL", "Mathematical structures define algorithmic form", 0.9),
        ("Consciousness", "Perception", "FORMAL", "Consciousness provides the framework for perception", 0.75),

        # EMERGENT cause - arises from complexity
        ("Human Brain", "Consciousness", "EMERGENT", "Consciousness emerges from complex brain activity", 0.85),
        ("Emotion", "Intuition", "EMERGENT", "Intuition emerges from emotional processing", 0.7),
        ("Memory", "Imagination", "EMERGENT", "Imagination emerges from memory recombination", 0.8),
    ]

    now = datetime.utcnow().isoformat()
    created = 0
    for source_name, target_name, ctype, desc, conf in links:
        if source_name in root_map and target_name in root_map:
            link_id = str(uuid.uuid4())
            try:
                db.execute_write(
                    """
                    INSERT INTO causality_links (id, source_entity_id, target_entity_id, causality_type, description, confidence, inferred_by, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (link_id, root_map[source_name], root_map[target_name], ctype, desc, conf, "sample_data", now, now)
                )
                created += 1
            except Exception as e:
                print(f"  Skipping link '{source_name} -> {target_name}': {e}")

    print(f"Created {created} sample causality links")


def create_epistemic_data():
    """Create sample epistemic annotations"""
    db = DatabaseManager(get_db_path("epistemic.db"))

    # Ensure table exists
    db.execute_script("""
        CREATE TABLE IF NOT EXISTS epistemic_annotations (
            id TEXT PRIMARY KEY,
            entity_id TEXT NOT NULL,
            basis TEXT NOT NULL CHECK(basis IN ('axiomatic', 'empirical', 'consensus', 'speculative')),
            certainty REAL DEFAULT 0.5,
            source TEXT,
            note TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_epistemic_entity ON epistemic_annotations(entity_id);
        CREATE INDEX IF NOT EXISTS idx_epistemic_basis ON epistemic_annotations(basis);
    """)

    # Get root IDs
    roots_db = DatabaseManager(get_db_path("roots.db"))
    roots = roots_db.execute("SELECT id, name FROM roots")
    root_map = {r['name']: r['id'] for r in roots}

    # Sample epistemic annotations
    annotations = [
        # Axiomatic - self-evident truths
        ("Mathematics", "axiomatic", 1.0, "Mathematical Logic", "Mathematical axioms are foundational truths"),
        ("Algorithm", "axiomatic", 0.95, "Computer Science Theory", "Algorithmic correctness can be formally proven"),
        ("Entropy", "axiomatic", 0.95, "Thermodynamics", "Second law of thermodynamics is fundamental"),

        # Empirical - based on observation/experiment
        ("Mount Everest", "empirical", 1.0, "Geological Survey", "Height measured by satellite and ground surveys"),
        ("DNA Molecule", "empirical", 1.0, "Molecular Biology", "Structure confirmed by X-ray crystallography"),
        ("Human Brain", "empirical", 0.95, "Neuroscience Research", "Based on neuroimaging and clinical studies"),
        ("Solar System", "empirical", 1.0, "Astronomical Observation", "Confirmed by centuries of observation"),
        ("Tiger", "empirical", 1.0, "Biological Classification", "Taxonomically classified through observation"),

        # Consensus - agreed upon by experts
        ("Democracy", "consensus", 0.85, "Political Philosophy", "Definition agreed upon by political scientists"),
        ("Justice", "consensus", 0.75, "Legal Philosophy", "Concept debated but general principles agreed"),
        ("Grammar", "consensus", 0.9, "Linguistics", "Grammatical rules established by linguistic consensus"),
        ("Economic Value", "consensus", 0.8, "Economics", "Value theories have broad economic consensus"),

        # Speculative - hypothetical/uncertain
        ("Consciousness", "speculative", 0.6, "Philosophy of Mind", "Nature of consciousness still debated"),
        ("Intuition", "speculative", 0.5, "Cognitive Science", "Mechanisms of intuition not fully understood"),
        ("Atlantis", "speculative", 0.3, "Historical Speculation", "Historical existence not proven"),
    ]

    now = datetime.utcnow().isoformat()
    created = 0
    for name, basis, certainty, source, note in annotations:
        if name in root_map:
            ann_id = str(uuid.uuid4())
            try:
                db.execute_write(
                    """
                    INSERT INTO epistemic_annotations (id, entity_id, basis, certainty, source, note, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (ann_id, root_map[name], basis, certainty, source, note, now, now)
                )
                created += 1
            except Exception as e:
                print(f"  Skipping annotation for '{name}': {e}")

    print(f"Created {created} sample epistemic annotations")


def create_mmo_data():
    """Create sample MMO classes and slots"""
    db = DatabaseManager(get_db_path("mmo.db"))

    # Ensure tables exist
    db.execute_script("""
        CREATE TABLE IF NOT EXISTS mmo_classes (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            parent_id TEXT,
            level INTEGER DEFAULT 0,
            weight REAL DEFAULT 1.0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_mmo_classes_name ON mmo_classes(name);
        CREATE INDEX IF NOT EXISTS idx_mmo_classes_parent ON mmo_classes(parent_id);

        CREATE TABLE IF NOT EXISTS mmo_slots (
            id TEXT PRIMARY KEY,
            class_id TEXT NOT NULL,
            name TEXT NOT NULL,
            data_type TEXT DEFAULT 'string',
            required INTEGER DEFAULT 0,
            cardinality TEXT DEFAULT 'single',
            description TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (class_id) REFERENCES mmo_classes(id)
        );
        CREATE INDEX IF NOT EXISTS idx_mmo_slots_class ON mmo_slots(class_id);
    """)

    now = datetime.utcnow().isoformat()

    # Sample MMO classes
    classes = [
        ("Entity", "Top-level ontological entity", None, 0, 1.0),
        ("PhysicalEntity", "Spatially extended entities", "Entity", 1, 1.0),
        ("AbstractEntity", "Non-physical concepts", "Entity", 1, 1.0),
        ("MentalEntity", "Mind-dependent entities", "Entity", 1, 0.9),
        ("FictiveEntity", "Fictional or hypothetical entities", "Entity", 1, 0.8),
        ("LivingOrganism", "Biological life forms", "PhysicalEntity", 2, 1.0),
        ("NaturalPhenomenon", "Natural occurrences", "PhysicalEntity", 2, 0.95),
        ("GeographicFeature", "Landforms and water bodies", "PhysicalEntity", 2, 1.0),
        ("Concept", "Abstract ideas", "AbstractEntity", 2, 1.0),
        ("Property", "Attributes and characteristics", "AbstractEntity", 2, 0.9),
    ]

    class_ids = {}
    for name, desc, parent_name, level, weight in classes:
        class_id = str(uuid.uuid4())
        parent_id = class_ids.get(parent_name) if parent_name else None
        try:
            db.execute_write(
                """
                INSERT INTO mmo_classes (id, name, description, parent_id, level, weight, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (class_id, name, desc, parent_id, level, weight, now, now)
            )
            class_ids[name] = class_id
        except Exception as e:
            print(f"  Skipping class '{name}': {e}")

    print(f"Created {len(classes)} MMO classes")

    # Sample slots for Entity class
    entity_id = class_ids.get("Entity")
    if entity_id:
        slots = [
            ("name", "string", 1, "single", "Entity name"),
            ("description", "string", 0, "single", "Entity description"),
            ("root_type", "enum", 1, "single", "Root type classification"),
            ("confidence", "float", 0, "single", "Confidence score"),
            ("source", "string", 0, "single", "Information source"),
            ("relations", "relation", 0, "multiple", "Related entities"),
        ]

        for name, dtype, required, card, desc in slots:
            slot_id = str(uuid.uuid4())
            try:
                db.execute_write(
                    """
                    INSERT INTO mmo_slots (id, class_id, name, data_type, required, cardinality, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (slot_id, entity_id, name, dtype, required, card, desc, now, now)
                )
            except Exception as e:
                print(f"  Skipping slot '{name}': {e}")

        print(f"Created {len(slots)} MMO slots")


def main():
    print("=" * 60)
    print("OmniCore Platform v10 - Sample Data Initialization")
    print("=" * 60)
    print()

    # Ensure data directory exists
    data_dir = project_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    print("Creating sample data...")
    print()

    print("[1/4] Creating Root Entities...")
    create_roots_data()

    print("\n[2/4] Creating Causality Links...")
    create_causality_data()

    print("\n[3/4] Creating Epistemic Annotations...")
    create_epistemic_data()

    print("\n[4/4] Creating MMO Classes and Slots...")
    create_mmo_data()

    print()
    print("=" * 60)
    print("Sample data initialization complete!")
    print()
    print("You can now start the OmniCore platform and explore the data")
    print("in the dashboard at http://192.168.1.3:3000 (or localhost:3000)")
    print("=" * 60)


if __name__ == "__main__":
    main()
