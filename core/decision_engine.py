from domain.models import Decision

class DecisionEngine:
    """
    Dynamic irrigation decision engine based on stress index and soil moisture.
    Provides proportional irrigation for moderate stress and full irrigation for high stress.
    """

    def __init__(self, threshold_low: float = 0.3, threshold_high: float = 0.6, max_irrigation_mm: float = 15.0):
        """
        Args:
            threshold_low: stress below this → no irrigation
            threshold_high: stress above this → maximum irrigation
            max_irrigation_mm: upper limit of irrigation in mm per day
        """
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high
        self.max_irrigation_mm = max_irrigation_mm

    def evaluate(self, stress_index: float, soil_moisture_mm: float, field_capacity_mm: float) -> Decision:
        """
        Evaluate the irrigation need based on stress index and soil moisture.

        Args:
            stress_index: current stress ratio (0 = no stress, 1 = max stress)
            soil_moisture_mm: current soil moisture in mm
            field_capacity_mm: maximum soil moisture in mm

        Returns:
            Decision object with irrigation_mm and reason
        """
        if stress_index < self.threshold_low:
            irrigation_mm = 0.0
            reason = f"Stress {stress_index:.2f} below low threshold {self.threshold_low:.2f}: no irrigation"
        elif stress_index > self.threshold_high:
            irrigation_mm = min(self.max_irrigation_mm, field_capacity_mm - soil_moisture_mm)
            reason = f"Stress {stress_index:.2f} above high threshold {self.threshold_high:.2f}: full irrigation"
        else:
            # Proportional irrigation for moderate stress
            ratio = (stress_index - self.threshold_low) / (self.threshold_high - self.threshold_low)
            irrigation_mm = min(self.max_irrigation_mm, ratio * (field_capacity_mm - soil_moisture_mm))
            reason = f"Stress {stress_index:.2f} moderate: proportional irrigation {irrigation_mm:.1f} mm"

        irrigation_mm = max(irrigation_mm, 0.0)
        return Decision(irrigation_mm=round(irrigation_mm, 1), reason=reason)
