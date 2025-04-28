import requests
import json
import logging
import os
from typing import Dict, List, Optional
from app.config.config import NOMINATIM_BASE_URL
from app.utils.cache_utils import read_cache, write_cache

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CityService:
    def __init__(self):
        self.base_url = NOMINATIM_BASE_URL
        self.cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'cache', 'cities')
        os.makedirs(self.cache_dir, exist_ok=True)

    def search_cities(self, query: str) -> List[Dict]:
        """Search for cities using Nominatim API"""
        try:
            # Check cache first
            cache_key = f"search_{query.lower().replace(' ', '_')}"
            cached_data = read_cache(cache_key, self.cache_dir)
            if cached_data:
                return cached_data

            # Prepare request parameters
            params = {
                'q': query,
                'format': 'json',
                'addressdetails': 1,
                'limit': 10,
                'countrycodes': 'ps,il',  # Palestine and Israel
                'featuretype': 'city,town,village'
            }

            # Make request to Nominatim API
            response = requests.get(
                f"{self.base_url}/search",
                params=params,
                headers={'User-Agent': 'RoadMap/1.0'}
            )
            
            if response.status_code != 200:
                logger.error(f"Error from Nominatim API: {response.status_code}")
                return []

            # Parse response
            results = response.json()
            
            # Format results for Select2
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'id': f"{result['lat']},{result['lon']}",
                    'text': result['display_name'],
                    'latitude': float(result['lat']),
                    'longitude': float(result['lon'])
                })
            
            # Cache the results
            write_cache(cache_key, formatted_results, self.cache_dir)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching cities: {e}")
            return []

    def get_city_info(self, lat: float, lon: float) -> Optional[Dict]:
        """Get detailed information about a city using Nominatim API"""
        try:
            # Check cache first
            cache_key = f"city_{lat}_{lon}"
            cached_data = read_cache(cache_key, self.cache_dir)
            if cached_data:
                return cached_data

            # Prepare request parameters
            params = {
                'lat': lat,
                'lon': lon,
                'format': 'json',
                'addressdetails': 1
            }

            # Make request to Nominatim API
            response = requests.get(
                f"{self.base_url}/reverse",
                params=params,
                headers={'User-Agent': 'RoadMap/1.0'}
            )
            
            if response.status_code != 200:
                logger.error(f"Error from Nominatim API: {response.status_code}")
                return None

            # Parse response
            result = response.json()
            
            # Extract relevant information
            city_info = {
                'name': result.get('display_name', ''),
                'latitude': float(result.get('lat', 0)),
                'longitude': float(result.get('lon', 0)),
                'country': result.get('address', {}).get('country', ''),
                'country_code': result.get('address', {}).get('country_code', ''),
                'state': result.get('address', {}).get('state', ''),
                'county': result.get('address', {}).get('county', ''),
                'city': result.get('address', {}).get('city', '') or 
                        result.get('address', {}).get('town', '') or 
                        result.get('address', {}).get('village', '')
            }
            
            # Cache the results
            write_cache(cache_key, city_info, self.cache_dir)
            
            return city_info
            
        except Exception as e:
            logger.error(f"Error getting city info: {e}")
            return None 