# core/simulator.py
from domain.models import SoilState
from domain.soil import SoilProfile, CropProfile


class SoilTwinSimulator:
    def __init__(
        self,
        soil: SoilProfile,
        crop: CropProfile,
        initial_moisture_mm: float
    ):
        self.soil = soil
        self.crop = crop
        self.soil_moisture_mm = initial_moisture_mm
        self.memory_factor = 0.0
        self.day = 0

    def step(
        self,
        et0_mm: float,
        rainfall_mm: float,
        irrigation_mm: float
    ) -> SoilState:
        self.day += 1

        # 1. Water balance
        evapotranspiration = et0_mm * self.crop.kc
        self.soil_moisture_mm += rainfall_mm + irrigation_mm
        self.soil_moisture_mm -= evapotranspiration

        # Clamp
        self.soil_moisture_mm = max(
            0.0,
            min(self.soil_moisture_mm, self.soil.field_capacity_mm)
        )

        # 2. Stress Index
        stress_index = self._calculate_stress()

        # 3. Memory Factor (simple decay)
        self.memory_factor = 0.7 * self.memory_factor + 0.3 * stress_index

        # 4. Soil Health Score
        soil_health_score = max(
            0.0,
            100.0 * (1.0 - self.memory_factor)
        )

        return SoilState(
            day=self.day,
            soil_moisture_mm=self.soil_moisture_mm,
            stress_index=stress_index,
            memory_factor=self.memory_factor,
            soil_health_score=soil_health_score
        )
# core/simulator.py (تغییرات)
    def _calculate_stress(self) -> float:
        """
        Stress Index بین 0 تا 1، خطی بین Wilting Point و Field Capacity
        """
        fc = self.soil.field_capacity_mm
        wp = self.soil.wilting_point_mm
        sm = self.soil_moisture_mm

        if sm >= fc:
            return 0.0  # بدون تنش
        elif sm <= wp:
            return 1.0  # حداکثر تنش
        else:
            # خطی بین WP و FC
            return (fc - sm) / (fc - wp)
