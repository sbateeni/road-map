from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class VehicleSpecs:
    brand: str
    model: str
    year: int
    fuel_consumption: float
    engine_size: int
    cylinders: int
    transmission: str
    fuel_type: str
    horsepower: int
    torque: int
    acceleration: float
    top_speed: int
    fuel_tank: int
    safety_rating: str
    airbags: int
    safety_systems: str
    maintenance: Dict[str, Dict[str, str]]

    @classmethod
    def from_dict(cls, data: Dict) -> 'VehicleSpecs':
        return cls(
            brand=data['brand'],
            model=data['model'],
            year=data['year'],
            fuel_consumption=float(data['fuel_consumption']),
            engine_size=int(data['engine_size']),
            cylinders=int(data['cylinders']),
            transmission=data['transmission'],
            fuel_type=data['fuel_type'],
            horsepower=int(data['horsepower']),
            torque=int(data['torque']),
            acceleration=float(data['acceleration']),
            top_speed=int(data['top_speed']),
            fuel_tank=int(data['fuel_tank']),
            safety_rating=data['safety_rating'],
            airbags=int(data['airbags']),
            safety_systems=data['safety_systems'],
            maintenance=data['maintenance']
        )

    def to_dict(self) -> Dict:
        return {
            'brand': self.brand,
            'model': self.model,
            'year': self.year,
            'fuel_consumption': self.fuel_consumption,
            'engine_size': self.engine_size,
            'cylinders': self.cylinders,
            'transmission': self.transmission,
            'fuel_type': self.fuel_type,
            'horsepower': self.horsepower,
            'torque': self.torque,
            'acceleration': self.acceleration,
            'top_speed': self.top_speed,
            'fuel_tank': self.fuel_tank,
            'safety_rating': self.safety_rating,
            'airbags': self.airbags,
            'safety_systems': self.safety_systems,
            'maintenance': self.maintenance
        } 