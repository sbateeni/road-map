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
import re
import requests

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

# قائمة المدن الفلسطينية
PALESTINIAN_CITIES = {
    'رام الله': {'lat': 31.9025, 'lon': 35.2061, 'country': 'فلسطين'},
    'جنين': {'lat': 32.4573, 'lon': 35.2888, 'country': 'فلسطين'},
    'نابلس': {'lat': 32.2222, 'lon': 35.2544, 'country': 'فلسطين'},
    'الخليل': {'lat': 31.5326, 'lon': 35.0998, 'country': 'فلسطين'},
    'بيت لحم': {'lat': 31.7054, 'lon': 35.2024, 'country': 'فلسطين'},
    'أريحا': {'lat': 31.8575, 'lon': 35.4447, 'country': 'فلسطين'},
    'غزة': {'lat': 31.5017, 'lon': 34.4668, 'country': 'فلسطين'},
    'طولكرم': {'lat': 32.3107, 'lon': 35.0286, 'country': 'فلسطين'},
    'قلقيلية': {'lat': 32.1908, 'lon': 34.9706, 'country': 'فلسطين'},
    'سلفيت': {'lat': 32.0833, 'lon': 35.1667, 'country': 'فلسطين'},
    'طوباس': {'lat': 32.3214, 'lon': 35.3697, 'country': 'فلسطين'},
    'القدس': {'lat': 31.7833, 'lon': 35.2167, 'country': 'فلسطين'}
}

def search_cities(query: str) -> list:
    """Search for cities using OpenRoute API"""
    if not query:
        return []

    try:
        # Check if it's a Palestinian city first
        if query in PALESTINIAN_CITIES:
            city_info = PALESTINIAN_CITIES[query]
            return [{
                "name": query,
                "english_name": query,  # Keep Arabic name for Palestinian cities
                "country": city_info['country'],
                "coordinates": {
                    "latitude": city_info['lat'],
                    "longitude": city_info['lon']
                }
            }]

        # Get OpenRoute API key
        api_key = os.getenv("OPENROUTE_API_KEY")
        if not api_key:
            logger.error("OpenRoute API key not found")
            return []

        # Prepare the request to OpenRoute Geocoding API
        headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json'
        }
        
        # Use the geocoding endpoint
        url = 'https://api.openrouteservice.org/geocode/search'
        params = {
            'text': query,
            'size': 5,
            'lang': 'ar',
            'layers': 'locality,localadmin,country'
        }

        # Make the request
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            logger.error(f"OpenRoute API error: {response.status_code}")
            return []

        data = response.json()
        if not data.get('features'):
            return []

        # Process the results
        cities = []
        for feature in data['features']:
            properties = feature['properties']
            geometry = feature['geometry']
            
            # Get country information
            country_info = get_country_info(geometry['coordinates'][1], geometry['coordinates'][0])
            if country_info:
                cities.append({
                    "name": properties.get('name', ''),
                    "english_name": properties.get('name', ''),
                    "country": country_info['country'],
                    "coordinates": {
                        "latitude": geometry['coordinates'][1],
                        "longitude": geometry['coordinates'][0]
                    }
                })

        return cities

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
                # Default fuel prices based on country
                if country_info['country'].lower() in ['united arab emirates', 'uae', 'الإمارات العربية المتحدة']:
                    country_info['fuel_prices'] = {
                        '95': 3.18,
                        '91': 3.03,
                        'diesel': 3.29
                    }
                elif country_info['country'].lower() in ['palestine', 'فلسطين']:
                    country_info['fuel_prices'] = {
                        '95': 7.7,
                        '91': 7.2,
                        'diesel': 7.2
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
                        # Default fuel prices based on country
                        if country_info['country'].lower() in ['united arab emirates', 'uae', 'الإمارات العربية المتحدة']:
                            country_info['fuel_prices'] = {
                                '95': 3.18,
                                '91': 3.03,
                                'diesel': 3.29
                            }
                        elif country_info['country'].lower() in ['palestine', 'فلسطين']:
                            country_info['fuel_prices'] = {
                                '95': 7.7,
                                '91': 7.2,
                                'diesel': 7.2
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
        # Check if it's a Palestinian city
        if address in PALESTINIAN_CITIES:
            city_info = PALESTINIAN_CITIES[address]
            coords = {
                "latitude": city_info['lat'],
                "longitude": city_info['lon'],
                "address": address
            }
            
            # Add country info for Palestinian cities
            coords["country_info"] = {
                "country": "فلسطين",
                "currency": {
                    "name": "شيكل إسرائيلي",
                    "code": "ILS",
                    "symbol": "₪"
                },
                "fuel_prices": {
                    "95": 7.7,
                    "91": 7.2,
                    "diesel": 7.2
                }
            }
            
            write_cache(cache_key, coords)
            return coords
        
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

def get_traffic_info(start_coords: dict, end_coords: dict) -> dict:
    """Get traffic information for a route using OpenRoute API"""
    try:
        api_key = os.getenv("OPENROUTE_API_KEY")
        if not api_key:
            logger.error("OpenRoute API key not found")
            return None

        headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json'
        }

        # Prepare the request body
        body = {
            "coordinates": [
                [start_coords['longitude'], start_coords['latitude']],
                [end_coords['longitude'], end_coords['latitude']]
            ],
            "instructions": True,
            "preference": "fastest",
            "units": "km",
            "language": "ar",
            "geometry_simplify": False,
            "continue_straight": False,
            "attributes": ["avgspeed", "percentage"]
        }

        # Make the request to OpenRoute Directions API
        url = 'https://api.openrouteservice.org/v2/directions/driving-car'
        response = requests.post(url, headers=headers, json=body)

        if response.status_code != 200:
            logger.error(f"OpenRoute API error: {response.status_code}")
            return None

        data = response.json()
        if not data.get('features'):
            return None

        # Process the traffic information
        traffic_info = {
            'segments': [],
            'total_distance': 0,
            'total_duration': 0
        }

        for feature in data['features']:
            properties = feature['properties']
            geometry = feature['geometry']
            
            # Calculate traffic segments
            segments = []
            for i in range(len(geometry['coordinates']) - 1):
                start = geometry['coordinates'][i]
                end = geometry['coordinates'][i + 1]
                
                # Get traffic data for this segment
                segment_traffic = {
                    'start': {'lon': start[0], 'lat': start[1]},
                    'end': {'lon': end[0], 'lat': end[1]},
                    'speed': properties.get('avgspeed', 0),
                    'percentage': properties.get('percentage', 0)
                }
                
                # Determine traffic level
                if segment_traffic['speed'] < 20:
                    segment_traffic['traffic_level'] = 'heavy'  # Red
                elif segment_traffic['speed'] < 40:
                    segment_traffic['traffic_level'] = 'moderate'  # Orange
                else:
                    segment_traffic['traffic_level'] = 'light'  # Blue
                
                segments.append(segment_traffic)
            
            traffic_info['segments'] = segments
            traffic_info['total_distance'] = properties.get('distance', 0)
            traffic_info['total_duration'] = properties.get('duration', 0)

        return traffic_info

    except Exception as e:
        logger.error(f"Error getting traffic info: {e}")
        return None

def get_route_with_traffic(start_coords: dict, end_coords: dict) -> dict:
    """Get route information with traffic data"""
    try:
        # Get basic route information
        route_info = get_route(start_coords, end_coords)
        if not route_info:
            return None

        # Get traffic information
        traffic_info = get_traffic_info(start_coords, end_coords)
        if not traffic_info:
            return route_info

        # Combine route and traffic information
        route_info['traffic'] = traffic_info
        return route_info

    except Exception as e:
        logger.error(f"Error getting route with traffic: {e}")
        return None

def get_route(start_coords: dict, end_coords: dict) -> dict:
    """Get route information using OpenRoute API"""
    try:
        api_key = os.getenv("OPENROUTE_API_KEY")
        if not api_key:
            logger.error("OpenRoute API key not found")
            return None

        headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json'
        }

        # Validate coordinates
        try:
            start_lat = float(start_coords['latitude'])
            start_lon = float(start_coords['longitude'])
            end_lat = float(end_coords['latitude'])
            end_lon = float(end_coords['longitude'])
        except (KeyError, ValueError) as e:
            logger.error(f"Invalid coordinates format: {e}")
            return None

        # Prepare the request body with correct coordinate format
        body = {
            "coordinates": [
                [start_lon, start_lat],
                [end_lon, end_lat]
            ],
            "instructions": True,
            "preference": "fastest",
            "units": "km",
            "language": "ar",
            "geometry_simplify": False,
            "continue_straight": False
        }

        # Make the request to OpenRoute Directions API
        url = 'https://api.openrouteservice.org/v2/directions/driving-car'
        response = requests.post(url, headers=headers, json=body)

        if response.status_code != 200:
            logger.error(f"OpenRoute API error: {response.status_code}")
            logger.error(f"Response content: {response.text}")
            return None

        data = response.json()
        if not data.get('features'):
            logger.error("No route features found in response")
            return None

        # Process the route information
        route_info = {
            'distance': 0,
            'duration': 0,
            'geometry': []
        }

        for feature in data['features']:
            properties = feature['properties']
            geometry = feature['geometry']
            
            route_info['distance'] = properties.get('distance', 0)
            route_info['duration'] = properties.get('duration', 0)
            route_info['geometry'] = geometry['coordinates']

        return route_info

    except Exception as e:
        logger.error(f"Error getting route: {e}")
        return None 