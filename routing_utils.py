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
            options={
                "avoid_features": ["highways", "tollways"] if route_type == "مسار الضفة الغربية فقط" else []
            }
        )
        
        # Process routes
        processed_routes = []
        
        # Check if routes is a list or a single route
        if isinstance(routes, list):
            route_features = routes
        else:
            route_features = [routes]
        
        for route in route_features:
            if 'features' in route:
                for feature in route['features']:
                    processed_route = {
                        'distance': feature['properties']['segments'][0]['distance'] / 1000,  # Convert to km
                        'duration': feature['properties']['segments'][0]['duration'] / 60,  # Convert to minutes
                        'geometry': feature['geometry']['coordinates']
                    }
                    processed_routes.append(processed_route)
            else:
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