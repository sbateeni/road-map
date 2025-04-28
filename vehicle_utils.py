import google.generativeai as genai
import json
import logging
from config import GEMINI_API_KEY, VEHICLE_CACHE_DIR
from cache_utils import read_cache, write_cache, get_vehicle_cache_key
from typing import Dict, Optional, List
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_vehicle_cache_key(brand: str, model: str, year: int) -> str:
    """Generate cache key for vehicle data"""
    return f"{brand.lower()}_{model.lower()}_{year}"

def clean_json_response(text: str) -> str:
    """Clean and format JSON response from Gemini API"""
    # Remove any markdown code block markers
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    
    # Remove any leading/trailing whitespace
    text = text.strip()
    
    # If the response is wrapped in a code block, extract just the JSON
    if text.startswith('{') and text.endswith('}'):
        return text
    elif text.startswith('[') and text.endswith(']'):
        return text
    
    # Try to find JSON-like structure
    json_match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
    if json_match:
        return json_match.group(1)
    
    return text

def get_vehicle_models(brand: str, api_key: str) -> List[str]:
    """Get list of models for a specific brand using Gemini API"""
    try:
        # Configure Gemini API
        logger.info("Configuring Gemini API...")
        genai.configure(api_key=api_key)
        
        # Initialize model
        logger.info("Initializing Gemini model...")
        gemini_model = genai.GenerativeModel('models/gemini-2.0-flash-001')
        
        # Create prompt
        prompt = f"""
        Please provide a list of car models for the brand {brand}.
        Return ONLY a JSON array of strings, nothing else.
        Example: ["Model 1", "Model 2", "Model 3"]
        """
        
        # Get response from Gemini
        logger.info(f"Sending prompt to Gemini for {brand} models...")
        response = gemini_model.generate_content(prompt)
        
        if not response or not response.text:
            logger.error("Received empty response from Gemini")
            return []
        
        # Clean and parse response
        try:
            cleaned_text = clean_json_response(response.text)
            models = json.loads(cleaned_text)
            if isinstance(models, list):
                return models
            else:
                logger.error(f"Expected list but got {type(models)}")
                return []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.error(f"Response text: {response.text}")
            return []
    except Exception as e:
        logger.error(f"Error getting vehicle models: {e}")
        return []

def get_vehicle_specs(brand: str, model: str, year: int, api_key: str) -> dict:
    """Get vehicle specifications using Gemini API"""
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
        - معدل استهلاك الوقود في المدينة (لتر/100 كم)
        - معدل استهلاك الوقود على الطرق السريعة (لتر/100 كم)
        - معدل استهلاك الوقود المختلط (لتر/100 كم)
        - كفاءة استهلاك الوقود (كم/لتر)
        - مواصفات المحرك
        - الأبعاد
        - ميزات الأمان
        - تفاصيل تقنية أخرى ذات صلة
        
        قم بتنسيق الاستجابة ككائن JSON بالهيكل التالي:
        {{
            "specifications": {{
                "fuel_consumption": {{
                    "city": float,
                    "highway": float,
                    "combined": float,
                    "efficiency": float
                }},
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
        }}
        
        تأكد من أن الاستجابة تحتوي على كائن JSON فقط، بدون أي نص إضافي.
        """
        
        # Get response from Gemini
        logger.info(f"Sending prompt to Gemini for {brand} {model} {year}...")
        response = gemini_model.generate_content(prompt)
        
        if not response or not response.text:
            logger.error("Received empty response from Gemini")
            return None
        
        # Clean and parse response
        try:
            cleaned_text = clean_json_response(response.text)
            specs = json.loads(cleaned_text)
            if isinstance(specs, dict) and 'specifications' in specs:
                return specs
            else:
                logger.error(f"Invalid specs format: {specs}")
                return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.error(f"Response text: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error getting vehicle specs: {e}")
        return None

def extract_fuel_consumption(specs: dict) -> dict:
    """استخراج معلومات استهلاك الوقود من المواصفات"""
    try:
        if 'specifications' in specs and 'fuel_consumption' in specs['specifications']:
            return specs['specifications']['fuel_consumption']
        return None
    except Exception as e:
        print(f"خطأ في استخراج معلومات استهلاك الوقود: {e}")
        return None

def calculate_fuel_cost(distance_km: float, fuel_consumption: dict, fuel_price: float) -> dict:
    """Calculate fuel cost for a trip"""
    # استخدام معدل الاستهلاك المختلط إذا كان متوفراً، وإلا استخدم معدل المدينة
    consumption_rate = fuel_consumption.get('combined', fuel_consumption.get('city', 8.0))
    
    # حساب كمية الوقود المطلوبة
    fuel_needed = (distance_km / 100) * consumption_rate
    
    # حساب التكلفة الإجمالية
    total_cost = fuel_needed * fuel_price
    
    return {
        "fuel_needed_liters": round(fuel_needed, 2),
        "total_cost": round(total_cost, 2),
        "consumption_rate": consumption_rate,
        "efficiency": fuel_consumption.get('efficiency', 0)
    } 