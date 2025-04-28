import httpx
import json
import logging
import ssl
from typing import Dict, Optional, List
from app.config.config import OPENROUTE_API_KEY, OPENROUTE_BASE_URL, ROUTE_CACHE_DIR
from app.utils.cache_utils import read_cache, write_cache

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RouteService:
    def __init__(self):
        self.api_key = OPENROUTE_API_KEY
        self.headers = {
            'Authorization': self.api_key,
            'Content-Type': 'application/json'
        }
        # Create a custom SSL context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Configure client with custom SSL context
        self.client = None

    def _get_client(self):
        """Get or create a client instance"""
        if self.client is None:
            self.client = httpx.Client(
                timeout=30.0,
                verify=False,  # Disable SSL verification
                follow_redirects=True,
                http2=True
            )
        return self.client

    def get_route(self, start_coords: Dict, end_coords: Dict, route_type: str = 'fastest') -> Optional[Dict]:
        """Get route information using OpenRoute API"""
        try:
            # Check cache first
            cache_key = f"{start_coords['latitude']}_{start_coords['longitude']}_{end_coords['latitude']}_{end_coords['longitude']}_{route_type}"
            cached_data = read_cache(cache_key, ROUTE_CACHE_DIR)
            if cached_data:
                return cached_data

            # Prepare coordinates
            coordinates = [
                [float(start_coords['longitude']), float(start_coords['latitude'])],
                [float(end_coords['longitude']), float(end_coords['latitude'])]
            ]

            # Prepare request body
            body = {
                "coordinates": coordinates,
                "language": "en",
                "units": "km",
                "preference": route_type,
                "options": {
                    "avoid_borders": "all",
                    "avoid_highways": True
                }
            }

            # Add avoid_countries only for non-West Bank routes
            if route_type != 'west_bank':
                body["options"]["avoid_countries"] = ["ISR"]

            # Try different API endpoints
            endpoints = [
                f"{OPENROUTE_BASE_URL}/directions/driving-car",
                "https://api.openroute.com/api/v2/directions/driving-car",
                "https://api.openroute.com/v2/directions/driving-car"
            ]

            response = None
            client = self._get_client()
            for endpoint in endpoints:
                try:
                    response = client.post(
                        endpoint,
                        headers=self.headers,
                        json=body
                    )
                    response.raise_for_status()
                    break
                except httpx.HTTPError as e:
                    logger.warning(f"Failed to connect to {endpoint}: {str(e)}")
                    continue
                except httpx.RequestError as e:
                    logger.warning(f"Request error for {endpoint}: {str(e)}")
                    continue

            if not response:
                logger.error("All API endpoints failed")
                return None

            data = response.json()

            # Check if we have routes in the response
            if not data.get('routes'):
                logger.error("No routes found in response")
                return None

            # Process the route information
            route_info = {
                'distance': 0,
                'duration': 0,
                'geometry': [],
                'instructions': [],
                'traffic': {
                    'segments': [],
                    'total_distance': 0,
                    'total_duration': 0
                }
            }

            # Get the first route
            route = data['routes'][0]
            
            # Extract summary information
            summary = route.get('summary', {})
            route_info['distance'] = summary.get('distance', 0)
            route_info['duration'] = summary.get('duration', 0)

            # Extract geometry
            if 'geometry' in route:
                if isinstance(route['geometry'], str):
                    # Handle encoded polyline
                    from polyline import decode
                    route_info['geometry'] = decode(route['geometry'])
                else:
                    # Handle GeoJSON
                    route_info['geometry'] = route['geometry']['coordinates']

            # Extract instructions
            if 'segments' in route:
                for segment in route['segments']:
                    if 'steps' in segment:
                        for step in segment['steps']:
                            route_info['instructions'].append({
                                'type': step.get('type', ''),
                                'instruction': step.get('instruction', ''),
                                'distance': step.get('distance', 0),
                                'duration': step.get('duration', 0)
                            })

                    # Add traffic information for this segment
                    route_info['traffic']['segments'].append({
                        'start': {
                            'latitude': segment['start'][1],
                            'longitude': segment['start'][0]
                        },
                        'end': {
                            'latitude': segment['end'][1],
                            'longitude': segment['end'][0]
                        },
                        'distance': segment.get('distance', 0),
                        'duration': segment.get('duration', 0),
                        'traffic_level': self._calculate_traffic_level(
                            segment.get('duration', 0),
                            segment.get('distance', 0)
                        )
                    })

            # Update total traffic information
            route_info['traffic']['total_distance'] = route_info['distance']
            route_info['traffic']['total_duration'] = route_info['duration']

            # Cache the results
            write_cache(cache_key, route_info, ROUTE_CACHE_DIR)

            return route_info

        except Exception as e:
            logger.error(f"Error getting route: {str(e)}")
            return None

    def _calculate_traffic_level(self, duration: float, distance: float) -> str:
        """Calculate traffic level based on duration and distance"""
        if distance == 0:
            return 'unknown'
            
        # Calculate speed in km/h
        speed = (distance / 1000) / (duration / 3600)
        
        if speed < 20:
            return 'heavy'
        elif speed < 40:
            return 'moderate'
        else:
            return 'light' 