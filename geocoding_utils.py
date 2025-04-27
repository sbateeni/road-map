from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from cache_utils import read_cache, write_cache, get_geocode_cache_key
import time

def get_location_cache_key(address: str) -> str:
    """Generate cache key for location data"""
    return f"location_{address.lower().replace(' ', '_')}"

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
            write_cache(cache_key, coords)
            return coords
    except GeocoderTimedOut:
        time.sleep(1)  # Wait before retrying
        return get_coordinates(address)
    except Exception as e:
        print(f"Error getting coordinates: {e}")
        return None 