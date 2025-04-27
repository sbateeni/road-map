import google.generativeai as genai
from config import GEMINI_API_KEY
from cache_utils import read_cache, write_cache

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

def get_vehicle_specs(brand: str, model: str, year: int) -> dict:
    """Get vehicle specifications using Gemini API"""
    cache_key = f"{brand}_{model}_{year}"
    
    # Check cache first
    cached_data = read_cache(cache_key)
    if cached_data:
        return cached_data
    
    # Prepare prompt for Gemini
    prompt = f"""
    Please provide detailed specifications for the {year} {brand} {model} car.
    Focus on:
    1. Fuel consumption (L/100km)
    2. Engine specifications
    3. Dimensions
    4. Safety features
    5. Performance metrics
    
    Format the response as a JSON object with these keys:
    - fuel_consumption
    - engine
    - dimensions
    - safety
    - performance
    """
    
    # Get response from Gemini
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    
    # Parse and cache the response
    specs = response.text
    write_cache(cache_key, specs)
    
    return specs 