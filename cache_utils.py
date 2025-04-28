import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

# Cache settings
CACHE_EXPIRY = 3600  # 1 hour in seconds
CACHE_ENABLED = True

# Cache directories
CACHE_DIR = Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache'))  # Use relative path
VEHICLE_CACHE_DIR = CACHE_DIR / "vehicles"
GEOCODE_CACHE_DIR = CACHE_DIR / "geocode"
ROUTE_CACHE_DIR = CACHE_DIR / "routes"

def ensure_cache_dir():
    """Ensure cache directories exist"""
    for dir_path in [CACHE_DIR, VEHICLE_CACHE_DIR, GEOCODE_CACHE_DIR, ROUTE_CACHE_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)

# Ensure cache directories exist on import
ensure_cache_dir()

def get_cache_path(key: str) -> Path:
    """Get cache file path for a key"""
    return CACHE_DIR / f"{key}.json"

def read_cache(key: str) -> dict:
    """Read data from cache if exists and not expired"""
    if not CACHE_ENABLED:
        return None
        
    cache_path = get_cache_path(key)
    if cache_path.exists():
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Check if cache is expired
                if 'timestamp' in data:
                    cache_time = datetime.fromisoformat(data['timestamp'])
                    if (datetime.now() - cache_time).total_seconds() > CACHE_EXPIRY:
                        return None
                return data
        except Exception as e:
            print(f"Error reading cache: {e}")
    return None

def write_cache(key: str, data: dict):
    """Write data to cache with timestamp"""
    if not CACHE_ENABLED:
        return
        
    ensure_cache_dir()
    cache_path = get_cache_path(key)
    try:
        # Add timestamp to cache data
        if isinstance(data, dict):
            data['timestamp'] = datetime.now().isoformat()
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error writing cache: {e}")

def get_vehicle_cache_key(brand: str, model: str, year: int) -> str:
    """Generate cache key for vehicle data"""
    return f"vehicle_{brand.lower()}_{model.lower()}_{year}"

def get_geocode_cache_key(address: str) -> str:
    """Generate cache key for geocoding data"""
    return f"geocode_{address.lower().replace(' ', '_')}"

def get_route_cache_key(origin: dict, destination: dict) -> str:
    """Generate cache key for route data"""
    return f"route_{origin['latitude']}_{origin['longitude']}_{destination['latitude']}_{destination['longitude']}" 