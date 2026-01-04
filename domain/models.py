# domain/models.py
from dataclasses import dataclass


@dataclass
class SoilState:
    day: int
    soil_moisture_mm: float
    stress_index: float
    memory_factor: float
    soil_health_score: float


@dataclass
class Decision:
    irrigation_mm: float
    reason: str
