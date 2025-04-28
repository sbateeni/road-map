import openrouteservice
from config import OPENROUTE_API_KEY
from cache_utils import read_cache, write_cache, get_route_cache_key
from openrouteservice.exceptions import ApiError
from geocoding_utils import get_coordinates
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure OpenRouteService client
client = openrouteservice.Client(key=OPENROUTE_API_KEY)

def get_routes(origin_coords: dict, destination_coords: dict, api_key: str, route_type: str = "أقصر مسار") -> list:
    """Get routes between two points using OpenRouteService"""
    cache_key = get_route_cache_key(origin_coords, destination_coords)
    
    # Check cache first
    cached_data = read_cache(cache_key)
    if cached_data:
        return cached_data
    
    # Initialize OpenRouteService client
    client = openrouteservice.Client(key=api_key)
    
    try:
        # Get routes
        routes = client.directions(
            coordinates=[
                [origin_coords['longitude'], origin_coords['latitude']],
                [destination_coords['longitude'], destination_coords['latitude']]
            ],
            profile='driving-car',
            format='geojson',
            alternatives=True,  # Get alternative routes
            options={
                "avoid_features": ["highways", "tollways"] if route_type == "مسار الضفة الغربية فقط" else []
            }
        )
        
        # Process routes
        processed_routes = []
        for route in routes['features']:
            # Check if route is in West Bank if required
            if route_type == "مسار الضفة الغربية فقط":
                # Check if route passes through West Bank
                is_west_bank = False
                for coord in route['geometry']['coordinates']:
                    # Check if coordinate is in West Bank
                    # Using more accurate coordinates for West Bank
                    if (34.5 <= coord[1] <= 35.5 and 31.0 <= coord[0] <= 32.5):
                        is_west_bank = True
                        break
                
                if not is_west_bank:
                    continue
            
            processed_route = {
                'distance': route['properties']['segments'][0]['distance'] / 1000,  # Convert to km
                'duration': route['properties']['segments'][0]['duration'] / 60,  # Convert to minutes
                'geometry': route['geometry']['coordinates']
            }
            processed_routes.append(processed_route)
        
        if not processed_routes:
            logger.warning("No valid routes found")
            return None
        
        # Cache the results
        write_cache(cache_key, processed_routes)
        return processed_routes
    except ApiError as e:
        logger.error(f"OpenRouteService API error: {e}")
        return None
    except Exception as e:
        logger.error(f"Error getting routes: {e}")
        return None 