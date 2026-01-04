# tests/test_simulator.py
import unittest
from core.simulator import SoilTwinSimulator
from domain.soil import LOAM, WHEAT

class TestSoilTwinSimulator(unittest.TestCase):

    def test_step_no_rain_irrigation(self):
        sim = SoilTwinSimulator(soil=LOAM, crop=WHEAT, initial_moisture_mm=LOAM.field_capacity_mm)
        state = sim.step(et0_mm=5.0, rainfall_mm=0.0, irrigation_mm=0.0)
        self.assertTrue(0.0 <= state.stress_index <= 1.0)
        self.assertTrue(0.0 <= state.soil_health_score <= 100.0)

    def test_memory_factor_accumulation(self):
        sim = SoilTwinSimulator(soil=LOAM, crop=WHEAT, initial_moisture_mm=LOAM.wilting_point_mm-10)
        states = [sim.step(5.0, 0.0, 0.0) for _ in range(3)]
        self.assertTrue(states[-1].memory_factor >= states[0].memory_factor)

if __name__ == "__main__":
    unittest.main()
