import openrouteservice
from config import OPENROUTE_API_KEY
from cache_utils import read_cache, write_cache, get_route_cache_key
from openrouteservice.exceptions import ApiError
from geocoding_utils import get_coordinates

# Configure OpenRouteService client
client = openrouteservice.Client(key=OPENROUTE_API_KEY)

def get_routes(origin_coords: dict, destination_coords: dict, api_key: str) -> list:
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
            format='geojson'
        )
        
        # Process routes
        processed_routes = []
        for route in routes['features']:
            processed_route = {
                'distance': route['properties']['segments'][0]['distance'] / 1000,  # Convert to km
                'duration': route['properties']['segments'][0]['duration'] / 60,  # Convert to minutes
                'geometry': route['geometry']['coordinates']
            }
            processed_routes.append(processed_route)
        
        # Cache the results
        write_cache(cache_key, processed_routes)
        return processed_routes
        
    except Exception as e:
        print(f"Error getting routes: {e}")
        return None 