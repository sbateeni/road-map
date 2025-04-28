import json
import os
import logging
from typing import Dict, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def read_cache(cache_key: str, cache_dir: str) -> Optional[Dict]:
    """Read data from cache"""
    try:
        cache_file = os.path.join(cache_dir, f"{cache_key}.json")
        if not os.path.exists(cache_file):
            return None
            
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading cache: {e}")
        return None

def write_cache(cache_key: str, data: Dict, cache_dir: str) -> bool:
    """Write data to cache"""
    try:
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        
        cache_file = os.path.join(cache_dir, f"{cache_key}.json")
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error writing cache: {e}")
        return False

def clear_cache(cache_dir: str) -> bool:
    """Clear all cached data"""
    try:
        if not os.path.exists(cache_dir):
            return True
            
        for file in os.listdir(cache_dir):
            if file.endswith('.json'):
                os.remove(os.path.join(cache_dir, file))
        return True
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return False 