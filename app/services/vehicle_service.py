import google.generativeai as genai
import json
import logging
from typing import Dict, Optional
from app.config.config import GEMINI_API_KEY, VEHICLE_CACHE_DIR
from app.models.vehicle import VehicleSpecs
from app.utils.cache_utils import read_cache, write_cache

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VehicleService:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('models/gemini-2.0-flash-001')

    def get_vehicle_specs(self, brand: str, model: str, year: int) -> Optional[VehicleSpecs]:
        """Get vehicle specifications using Gemini API"""
        try:
            # Check cache first
            cache_key = f"{brand.lower()}_{model.lower()}_{year}"
            cached_data = read_cache(cache_key, VEHICLE_CACHE_DIR)
            if cached_data:
                return VehicleSpecs.from_dict(cached_data)

            # Prepare prompt
            prompt = f"""Get detailed specifications for a {year} {brand} {model} car. Include:
            1. Basic specs: brand, model, year, fuel consumption (L/100km)
            2. Technical specs: engine size (cc), cylinders, transmission, fuel type
            3. Performance: horsepower, torque (Nm), 0-100 km/h acceleration (seconds), top speed (km/h), fuel tank capacity (L)
            4. Safety: safety rating, number of airbags, safety systems
            5. Maintenance: oil change interval (km and time), tire change interval (km and time), service interval (km and time)
            
            Format the response as a JSON object with these exact keys:
            {{
                "brand": "{brand}",
                "model": "{model}",
                "year": {year},
                "fuel_consumption": float,
                "engine_size": integer,
                "cylinders": integer,
                "transmission": "string",
                "fuel_type": "string",
                "horsepower": integer,
                "torque": integer,
                "acceleration": float,
                "top_speed": integer,
                "fuel_tank": integer,
                "safety_rating": "string",
                "airbags": integer,
                "safety_systems": "string",
                "maintenance": {{
                    "oil_change": {{ "distance": "string", "time": "string" }},
                    "tire_change": {{ "distance": "string", "time": "string" }},
                    "service": {{ "distance": "string", "time": "string" }}
                }}
            }}
            
            Important:
            - Return ONLY the JSON object, no additional text
            - Use exact values for brand, model, and year as provided
            - Ensure all numeric values are actual numbers, not strings
            """

            # Get response from Gemini
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                logger.error("Received empty response from Gemini")
                return None

            # Clean and parse response
            try:
                # Clean the response text
                cleaned_text = response.text.strip()
                if cleaned_text.startswith('```json'):
                    cleaned_text = cleaned_text[7:]
                if cleaned_text.endswith('```'):
                    cleaned_text = cleaned_text[:-3]
                cleaned_text = cleaned_text.strip()

                # Parse JSON
                specs_data = json.loads(cleaned_text)
                
                # Create VehicleSpecs object
                specs = VehicleSpecs.from_dict(specs_data)
                
                # Cache the results
                write_cache(cache_key, specs.to_dict(), VEHICLE_CACHE_DIR)
                
                return specs
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON: {e}")
                logger.error(f"Response text: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting vehicle specs: {e}")
            return None

    def calculate_fuel_cost(self, distance_km: float, fuel_consumption: float, fuel_price: float) -> Dict:
        """Calculate fuel cost for a trip"""
        try:
            # Calculate fuel needed
            fuel_needed = (distance_km / 100) * fuel_consumption
            
            # Calculate total cost
            total_cost = fuel_needed * fuel_price
            
            return {
                "fuel_needed_liters": round(fuel_needed, 2),
                "total_cost": round(total_cost, 2),
                "consumption_rate": fuel_consumption,
                "distance_km": distance_km,
                "fuel_price": fuel_price
            }
        except Exception as e:
            logger.error(f"Error calculating fuel cost: {e}")
            return None 