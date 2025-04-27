import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from cache_utils import read_cache, write_cache

def get_fuel_prices_cache_key(country: str) -> str:
    """Generate cache key for fuel prices"""
    return f"fuel_prices_{country.lower().replace(' ', '_')}"

def get_fuel_prices(country: str) -> dict:
    """Get current fuel prices for a country"""
    cache_key = get_fuel_prices_cache_key(country)
    
    # Check cache first (cache for 1 hour)
    cached_data = read_cache(cache_key)
    if cached_data and (datetime.now() - datetime.fromisoformat(cached_data['timestamp'])).total_seconds() < 3600:
        return cached_data['prices']
    
    try:
        if country.lower() in ['فلسطين', 'palestine', 'west bank']:
            # Get fuel prices for Palestine
            prices = get_palestine_fuel_prices()
        elif country.lower() in ['إسرائيل', 'israel']:
            # Get fuel prices for Israel
            prices = get_israel_fuel_prices()
        else:
            # Default prices if country not found
            prices = {
                '95': 0.0,
                '91': 0.0,
                'diesel': 0.0
            }
        
        # Cache the results with timestamp
        cache_data = {
            'prices': prices,
            'timestamp': datetime.now().isoformat()
        }
        write_cache(cache_key, cache_data)
        
        return prices
    except Exception as e:
        print(f"Error getting fuel prices: {e}")
        return None

def get_palestine_fuel_prices() -> dict:
    """Get current fuel prices for Palestine"""
    try:
        # Get prices from Palestinian Ministry of Energy website
        url = "https://www.moe.gov.ps/ar/fuel-prices"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract prices from the website
        # Note: This is a placeholder. You'll need to adjust the selectors based on the actual website structure
        prices = {
            '95': float(soup.find('div', {'class': 'price-95'}).text.strip()),
            '91': float(soup.find('div', {'class': 'price-91'}).text.strip()),
            'diesel': float(soup.find('div', {'class': 'price-diesel'}).text.strip())
        }
        
        return prices
    except Exception as e:
        print(f"Error getting Palestine fuel prices: {e}")
        # Return default prices if website is not accessible
        return {
            '95': 7.7,  # Default price for 95
            '91': 7.2,  # Default price for 91
            'diesel': 7.2  # Default price for diesel
        }

def get_israel_fuel_prices() -> dict:
    """Get current fuel prices for Israel"""
    try:
        # Get prices from Israeli Ministry of Energy website
        url = "https://www.gov.il/he/departments/fuel_prices"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract prices from the website
        # Note: This is a placeholder. You'll need to adjust the selectors based on the actual website structure
        prices = {
            '95': float(soup.find('div', {'class': 'price-95'}).text.strip()),
            '91': float(soup.find('div', {'class': 'price-91'}).text.strip()),
            'diesel': float(soup.find('div', {'class': 'price-diesel'}).text.strip())
        }
        
        return prices
    except Exception as e:
        print(f"Error getting Israel fuel prices: {e}")
        # Return default prices if website is not accessible
        return {
            '95': 7.83,  # Default price for 95
            '91': 7.65,  # Default price for 91
            'diesel': 7.8  # Default price for diesel
        } 