
import unittest
import tempfile
import shutil
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.mmo.store import MMOStore
from common.models import MMOClassCreate, MMOSlotCreate

class TestMMOStoreUnit(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "mmo_test.db")
        self.store = MMOStore(db_path=self.db_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_dynamic_weights_calculation(self):
        # 1. Create some data
        cls = self.store.create_class(MMOClassCreate(name="TestClass"))
        self.store.create_slot(MMOSlotCreate(
            name="testSlot", 
            domain_class_id=cls.id, 
            range_type="string"
        ))

        # 2. Initial Metrics Calculation
        metrics = self.store.calculate_metrics()
        
        print("\nWeights:", metrics.weights)
        print("Score:", metrics.mmo_score)
        print("Predictive Power:", metrics.predictive_power)

        # 3. Verify weights sum to 1.0 (approx)
        total_weight = sum(metrics.weights.values())
        self.assertAlmostEqual(total_weight, 1.0, places=4)

        # 4. Verify logic: equal predictive power -> equal weights
        # Default predictive power is 0.5 for all
        self.assertAlmostEqual(metrics.weights['completeness'], 0.2, places=2)
        
        # 5. Verify basic metrics are non-zero
        self.assertGreater(metrics.completeness, 0.0)
        self.assertGreater(metrics.coverage, 0.0)

if __name__ == '__main__':
    unittest.main()
