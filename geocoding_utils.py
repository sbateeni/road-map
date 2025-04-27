from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from cache_utils import read_cache, write_cache, get_geocode_cache_key
import time
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

# تحميل المتغيرات البيئية
load_dotenv()

# تكوين Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel('models/gemini-2.0-flash-001')

def get_location_cache_key(address: str) -> str:
    """Generate cache key for location data"""
    return f"location_{address.lower().replace(' ', '_')}"

def get_country_info(latitude: float, longitude: float) -> dict:
    """Get country information using Gemini API"""
    cache_key = f"country_info_{latitude}_{longitude}"
    
    # Check cache first
    cached_data = read_cache(cache_key)
    if cached_data:
        return cached_data
    
    # Create prompt
    prompt = f"""قم بتقديم معلومات عن البلد الذي يقع فيه الموقع التالي:
    خط العرض: {latitude}
    خط الطول: {longitude}
    
    يجب أن تتضمن المعلومات:
    - اسم البلد
    - العملة المستخدمة
    - أسعار الوقود المختلفة:
      * بنزين 95
      * بنزين 91
      * ديزل
    - سعر الوقود بالدولار الأمريكي
    
    قم بتنسيق الاستجابة ككائن JSON بالهيكل التالي:
    {{
        "country": string,
        "currency": {{
            "name": string,
            "code": string,
            "symbol": string
        }},
        "fuel_prices": {{
            "95": float,
            "91": float,
            "diesel": float,
            "usd": float
        }}
    }}"""
    
    # Get response from Gemini
    response = gemini_model.generate_content(prompt)
    
    # Parse and store response
    try:
        # Try to parse the response as JSON
        country_info = json.loads(response.text)
        write_cache(cache_key, country_info)
        return country_info
    except json.JSONDecodeError:
        # If parsing fails, try to extract JSON from the text
        try:
            # Find JSON-like structure in the text
            start_idx = response.text.find('{')
            end_idx = response.text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response.text[start_idx:end_idx]
                country_info = json.loads(json_str)
                write_cache(cache_key, country_info)
                return country_info
        except:
            pass
        
        print(f"Error parsing country info: {response.text}")
        return None
    except Exception as e:
        print(f"Error getting country info: {e}")
        return None

def get_coordinates(address: str) -> dict:
    """Get coordinates for an address using Nominatim"""
    cache_key = get_geocode_cache_key(address)
    
    # Check cache first
    cached_data = read_cache(cache_key)
    if cached_data:
        return cached_data
    
    # Initialize Nominatim
    geolocator = Nominatim(user_agent="road_map_app")
    
    try:
        # Get location
        location = geolocator.geocode(address)
        if location:
            coords = {
                "latitude": location.latitude,
                "longitude": location.longitude,
                "address": location.address
            }
            
            # Get country information
            country_info = get_country_info(location.latitude, location.longitude)
            if country_info:
                coords["country_info"] = country_info
            
            write_cache(cache_key, coords)
            return coords
    except GeocoderTimedOut:
        time.sleep(1)  # Wait before retrying
        return get_coordinates(address)
    except Exception as e:
        print(f"Error getting coordinates: {e}")
        return None 