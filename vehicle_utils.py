import google.generativeai as genai
import json
import logging
from config import GEMINI_API_KEY, VEHICLE_CACHE_DIR
from cache_utils import read_cache, write_cache, get_vehicle_cache_key
from typing import Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_vehicle_cache_key(brand: str, model: str, year: int) -> str:
    """Generate cache key for vehicle data"""
    return f"{brand.lower()}_{model.lower()}_{year}"

def get_vehicle_specs(brand: str, model: str, year: int, api_key: str) -> dict:
    """Get vehicle specifications using Gemini API"""
    cache_key = get_vehicle_cache_key(brand, model, year)
    
    # Check cache first
    cached_data = read_cache(cache_key)
    if cached_data:
        logger.info(f"Retrieved vehicle specs from cache for {brand} {model} {year}")
        return cached_data
    
    try:
        # Configure Gemini API
        logger.info("Configuring Gemini API...")
        genai.configure(api_key=api_key)
        
        # Initialize model
        logger.info("Initializing Gemini model...")
        gemini_model = genai.GenerativeModel('models/gemini-2.0-flash-001')
        
        # Create prompt
        prompt = f"""قم بتقديم مواصفات مفصلة لسيارة {year} {brand} {model}.
        يجب أن تتضمن:
        - معدل استهلاك الوقود (لتر/100 كم)
        - مواصفات المحرك
        - الأبعاد
        - ميزات الأمان
        - تفاصيل تقنية أخرى ذات صلة
        
        قم بتنسيق الاستجابة ككائن JSON بالهيكل التالي:
        {{
            "specifications": {{
                "fuel_consumption": float,
                "engine": {{
                    "type": string,
                    "displacement": string,
                    "power": string,
                    "torque": string
                }},
                "dimensions": {{
                    "length": string,
                    "width": string,
                    "height": string,
                    "wheelbase": string
                }},
                "safety_features": [string],
                "other_details": {{
                    "transmission": string,
                    "drivetrain": string,
                    "fuel_tank": string,
                    "weight": string
                }}
            }}
        }}"""
        
        # Get response from Gemini
        logger.info(f"Sending prompt to Gemini for {brand} {model} {year}...")
        response = gemini_model.generate_content(prompt)
        
        if not response or not response.text:
            logger.error("Received empty response from Gemini")
            return None
        
        # Parse and store response
        try:
            # Try to parse the response as JSON
            logger.info("Parsing response as JSON...")
            specs = json.loads(response.text)
            write_cache(cache_key, specs)
            logger.info(f"Successfully cached vehicle specs for {brand} {model} {year}")
            return specs
        except json.JSONDecodeError:
            # If parsing fails, try to extract JSON from the text
            logger.warning("Failed to parse response as JSON, attempting to extract JSON structure...")
            try:
                # Find JSON-like structure in the text
                start_idx = response.text.find('{')
                end_idx = response.text.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response.text[start_idx:end_idx]
                    specs = json.loads(json_str)
                    write_cache(cache_key, specs)
                    logger.info(f"Successfully extracted and cached vehicle specs for {brand} {model} {year}")
                    return specs
            except Exception as e:
                logger.error(f"Failed to extract JSON from response: {e}")
                logger.error(f"Response text: {response.text}")
                return None
    except Exception as e:
        logger.error(f"Error getting vehicle specs: {e}")
        return None

def extract_fuel_consumption(specs: dict) -> float:
    """استخراج معدل استهلاك الوقود من المواصفات"""
    try:
        # البحث عن معدل الاستهلاك في النص
        text = specs['specs'].lower()
        if 'لتر/100 كم' in text:
            # استخراج الرقم قبل "لتر/100 كم"
            parts = text.split('لتر/100 كم')
            for part in parts:
                if part.strip():
                    try:
                        return float(part.strip().split()[-1])
                    except:
                        continue
    except Exception as e:
        print(f"خطأ في استخراج معدل الاستهلاك: {e}")
    return None

def calculate_fuel_cost(distance_km: float, fuel_consumption: float, fuel_price: float) -> dict:
    """Calculate fuel cost for a trip"""
    fuel_needed = (distance_km / 100) * fuel_consumption
    total_cost = fuel_needed * fuel_price
    
    return {
        "fuel_needed_liters": round(fuel_needed, 2),
        "total_cost": round(total_cost, 2)
    } 