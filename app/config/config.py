import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
OPENROUTE_API_KEY = os.getenv('OPENROUTE_API_KEY')

# Cache settings
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache')
VEHICLE_CACHE_DIR = os.path.join(CACHE_DIR, 'vehicles')
ROUTE_CACHE_DIR = os.path.join(CACHE_DIR, 'routes')

# Create cache directories if they don't exist
os.makedirs(VEHICLE_CACHE_DIR, exist_ok=True)
os.makedirs(ROUTE_CACHE_DIR, exist_ok=True)

# API endpoints
OPENROUTE_BASE_URL = 'https://api.openroute.com/api/v2'
NOMINATIM_BASE_URL = 'https://nominatim.openstreetmap.org'

# Default settings
DEFAULT_FUEL_PRICE = 7.7  # ILS per liter
DEFAULT_CURRENCY = {
    'name': 'شيكل إسرائيلي',
    'code': 'ILS',
    'symbol': '₪'
}

# Logging configuration
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO' 