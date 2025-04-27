import os
from dotenv import load_dotenv

# تحميل المتغيرات البيئية
load_dotenv()

# إعدادات API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
OPENROUTE_API_KEY = os.getenv('OPENROUTE_API_KEY')

# إعدادات التخزين المؤقت
CACHE_DIR = '/tmp/cache'  # استخدام مجلد مؤقت في Streamlit Cloud
VEHICLE_CACHE_DIR = os.path.join(CACHE_DIR, 'vehicles')
GEOCODE_CACHE_DIR = os.path.join(CACHE_DIR, 'geocode')
ROUTE_CACHE_DIR = os.path.join(CACHE_DIR, 'routes')

# سعر الوقود (يمكن تحديثه من API)
FUEL_PRICE = 2.18  # ريال/لتر

# إنشاء مجلدات التخزين المؤقت
for dir_path in [CACHE_DIR, VEHICLE_CACHE_DIR, GEOCODE_CACHE_DIR, ROUTE_CACHE_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# Default fuel price (SAR per liter)
DEFAULT_FUEL_PRICE = 2.18

# Cache settings
CACHE_EXPIRY = 3600  # 1 hour in seconds
CACHE_ENABLED = True

# API endpoints
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OPENROUTE_URL = "https://api.openrouteservice.org/v2/directions/driving-car"

# Constants
FUEL_PRICE_PER_LITER = 2.18  # SAR per liter (example price)
DEFAULT_REGION = "Saudi Arabia"
DEFAULT_FUEL_CONSUMPTION = 8.0  # L/100km (default if not found in specs) 