import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from config import CACHE_EXPIRY

# Cache directories
CACHE_DIR = Path("cache")
VEHICLE_CACHE_DIR = CACHE_DIR / "vehicles"
GEOCODE_CACHE_DIR = CACHE_DIR / "geocode"
ROUTE_CACHE_DIR = CACHE_DIR / "routes"

def ensure_cache_dir():
    """Ensure cache directories exist"""
    for directory in [CACHE_DIR, VEHICLE_CACHE_DIR, GEOCODE_CACHE_DIR, ROUTE_CACHE_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

def get_cache_path(key: str) -> Path:
    """Get cache file path for a key"""
    return CACHE_DIR / f"{key}.json"

def read_cache(key: str) -> dict:
    """Read data from cache if exists"""
    cache_path = get_cache_path(key)
    if cache_path.exists():
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading cache: {e}")
    return None

def write_cache(key: str, data: dict):
    """Write data to cache"""
    ensure_cache_dir()
    cache_path = get_cache_path(key)
    try:
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