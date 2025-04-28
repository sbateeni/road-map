from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from cache_utils import read_cache, write_cache, get_geocode_cache_key
import time
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
from fuel_prices import get_fuel_prices
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# تحميل المتغيرات البيئية
load_dotenv()

# تكوين Gemini API
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    gemini_model = genai.GenerativeModel('models/gemini-2.0-flash-001')
except Exception as e:
    logger.error(f"Failed to configure Gemini API: {e}")
    gemini_model = None

# قائمة المدن الإماراتية
UAE_CITIES = {
    'دبي': 'Dubai',
    'ابو ظبي': 'Abu Dhabi',
    'الشارقة': 'Sharjah',
    'العين': 'Al Ain',
    'رأس الخيمة': 'Ras Al Khaimah',
    'أم القيوين': 'Umm Al Quwain',
    'عجمان': 'Ajman',
    'الفجيرة': 'Fujairah'
}

def search_cities(query: str) -> list:
    """Search for cities using Gemini API"""
    if not gemini_model:
        logger.error("Gemini model not configured")
        return []

    try:
        # Prepare prompt for Gemini
        prompt = f"""
        Please search for cities and locations that match the query: "{query}"
        Return the results as a JSON array of objects with this structure:
        [
            {{
                "name": "string",  # City name in Arabic
                "english_name": "string",  # City name in English
                "country": "string",  # Country name in Arabic
                "coordinates": {{
                    "latitude": float,
                    "longitude": float
                }}
            }}
        ]
        """
        
        # Get response from Gemini
        response = gemini_model.generate_content(prompt)
        
        if not response or not response.text:
            logger.error("Received empty response from Gemini")
            return []
        
        # Parse response
        try:
            # Try to parse the response as JSON
            cities = json.loads(response.text)
            return cities
        except json.JSONDecodeError:
            # If parsing fails, try to extract JSON from the text
            try:
                # Find JSON-like structure in the text
                start_idx = response.text.find('[')
                end_idx = response.text.rfind(']') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response.text[start_idx:end_idx]
                    cities = json.loads(json_str)
                    return cities
            except Exception as e:
                logger.error(f"Failed to extract JSON from response: {e}")
                logger.error(f"Response text: {response.text}")
                return []
    except Exception as e:
        logger.error(f"Error searching cities: {e}")
        return []

def get_location_cache_key(address: str) -> str:
    """Generate cache key for location data"""
    return f"location_{address.lower().replace(' ', '_')}"

def get_country_info(latitude: float, longitude: float) -> dict:
    """Get country information using Gemini API"""
    if not gemini_model:
        logger.error("Gemini model not configured")
        return None

    cache_key = f"country_info_{latitude}_{longitude}"
    
    # Check cache first
    cached_data = read_cache(cache_key)
    if cached_data:
        return cached_data
    
    try:
        # Prepare prompt for Gemini
        prompt = f"""
        Please provide information about the country at coordinates {latitude}, {longitude}.
        Include:
        1. Country name
        2. Currency (name, code, symbol)
        3. Current fuel prices (95, 91, diesel)
        
        Format the response as a JSON object with this structure:
        {{
            "country": "string",
            "currency": {{
                "name": "string",
                "code": "string",
                "symbol": "string"
            }},
            "fuel_prices": {{
                "95": float,
                "91": float,
                "diesel": float
            }}
        }}
        """
        
        # Get response from Gemini
        response = gemini_model.generate_content(prompt)
        
        if not response or not response.text:
            logger.error("Received empty response from Gemini")
            return None
        
        # Parse and store response
        try:
            # Try to parse the response as JSON
            country_info = json.loads(response.text)
            
            # Get real-time fuel prices
            fuel_prices = get_fuel_prices(country_info['country'])
            if fuel_prices:
                country_info['fuel_prices'] = fuel_prices
            else:
                # Default UAE fuel prices if API fails
                if country_info['country'].lower() in ['united arab emirates', 'uae', 'الإمارات العربية المتحدة']:
                    country_info['fuel_prices'] = {
                        '95': 3.18,
                        '91': 3.03,
                        'diesel': 3.29
                    }
                else:
                    country_info['fuel_prices'] = {
                        '95': 0.0,
                        '91': 0.0,
                        'diesel': 0.0
                    }
            
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
                    
                    # Get real-time fuel prices
                    fuel_prices = get_fuel_prices(country_info['country'])
                    if fuel_prices:
                        country_info['fuel_prices'] = fuel_prices
                    else:
                        # Default UAE fuel prices if API fails
                        if country_info['country'].lower() in ['united arab emirates', 'uae', 'الإمارات العربية المتحدة']:
                            country_info['fuel_prices'] = {
                                '95': 3.18,
                                '91': 3.03,
                                'diesel': 3.29
                            }
                        else:
                            country_info['fuel_prices'] = {
                                '95': 0.0,
                                '91': 0.0,
                                'diesel': 0.0
                            }
                    
                    write_cache(cache_key, country_info)
                    return country_info
            except Exception as e:
                logger.error(f"Failed to extract JSON from response: {e}")
                logger.error(f"Response text: {response.text}")
                return None
    except Exception as e:
        logger.error(f"Error getting country info: {e}")
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
            else:
                # Default UAE info if country info fails
                coords["country_info"] = {
                    "country": "الإمارات العربية المتحدة",
                    "currency": {
                        "name": "درهم إماراتي",
                        "code": "AED",
                        "symbol": "د.إ"
                    },
                    "fuel_prices": {
                        "95": 3.18,
                        "91": 3.03,
                        "diesel": 3.29
                    }
                }
            
            write_cache(cache_key, coords)
            return coords
    except GeocoderTimedOut:
        logger.warning(f"Geocoder timed out for address: {address}")
        time.sleep(1)  # Wait before retrying
        return get_coordinates(address)
    except GeocoderServiceError as e:
        logger.error(f"Geocoder service error: {e}")
        return None
    except Exception as e:
        logger.error(f"Error getting coordinates: {e}")
        return None 