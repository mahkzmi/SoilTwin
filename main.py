# main.py (تغییرات)
from core.simulator import SoilTwinSimulator
from core.decision_engine import DecisionEngine
from domain.soil import LOAM, WHEAT

def main():
    simulator = SoilTwinSimulator(
        soil=LOAM,
        crop=WHEAT,
        initial_moisture_mm=120.0
    )

    decision_engine = DecisionEngine(threshold_stress=0.5, irrigation_mm=15.0)

    for day in range(1, 11):
        state = simulator.step(
            et0_mm=5.0,
            rainfall_mm=0.0,
            irrigation_mm=0.0  # ابتدا بدون آبیاری
        )

        # گرفتن توصیه آبیاری
        decision = decision_engine.evaluate(state.stress_index)

        # اعمال آبیاری پیشنهادی
        state = simulator.step(
            et0_mm=5.0,
            rainfall_mm=0.0,
            irrigation_mm=decision.irrigation_mm
        )

        print(
            f"Day {state.day} | "
            f"Soil Moisture: {state.soil_moisture_mm:.1f} mm | "
            f"Stress: {state.stress_index:.2f} | "
            f"Memory: {state.memory_factor:.2f} | "
            f"Health: {state.soil_health_score:.1f} | "
            f"Irrigation: {decision.irrigation_mm} mm ({decision.reason})"
        )


if __name__ == "__main__":
    main()
