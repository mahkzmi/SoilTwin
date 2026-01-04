# tests/test_decision_engine.py
import unittest
from core.decision_engine import DecisionEngine

class TestDecisionEngine(unittest.TestCase):
    def test_no_irrigation_below_threshold(self):
        engine = DecisionEngine(threshold_stress=0.5)
        decision = engine.evaluate(0.3)
        self.assertEqual(decision.irrigation_mm, 0.0)

    def test_irrigation_above_threshold(self):
        engine = DecisionEngine(threshold_stress=0.5, irrigation_mm=12.0)
        decision = engine.evaluate(0.7)
        self.assertEqual(decision.irrigation_mm, 12.0)

if __name__ == "__main__":
    unittest.main()
