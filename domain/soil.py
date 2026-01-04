# domain/soil.py
from dataclasses import dataclass


@dataclass
class SoilProfile:
    name: str
    field_capacity_mm: float
    wilting_point_mm: float


@dataclass
class CropProfile:
    name: str
    kc: float  # Crop coefficient


# پروفایل‌های نمونه (MVP علمی)
LOAM = SoilProfile(
    name="Loam",
    field_capacity_mm=150.0,
    wilting_point_mm=60.0
)

WHEAT = CropProfile(
    name="Wheat",
    kc=1.05
)
