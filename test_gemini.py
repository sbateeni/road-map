import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_vehicle_specs(brand: str, model: str, year: int):
    """Test getting vehicle specifications from Gemini API"""
    try:
        # Get API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("Gemini API key not found")
            return

        # Configure Gemini API
        logger.info(f"Configuring Gemini API for {brand} {model} {year}")
        genai.configure(api_key=api_key)
        gemini_model = genai.GenerativeModel('models/gemini-2.0-flash-001')
        
        # Prepare prompt
        prompt = f"""
        Please provide detailed specifications for a {year} {brand} {model}.
        Include:
        1. Brand
        2. Model
        3. Year
        4. Fuel consumption (liters/100km)
        5. Engine size (cc)
        6. Number of cylinders
        7. Transmission type
        8. Fuel type
        
        Format the response as a JSON object with this structure:
        {{
            "brand": "{brand}",
            "model": "{model}",
            "year": {year},
            "fuel_consumption": float,
            "engine_size": integer,
            "cylinders": integer,
            "transmission": "string",
            "fuel_type": "string"
        }}
        
        Important:
        - Return ONLY the JSON object, no additional text
        - Use exact values for brand, model, and year as provided
        - Ensure all numeric values are actual numbers, not strings
        """
        
        logger.info("Sending prompt to Gemini API")
        # Get response from Gemini
        response = gemini_model.generate_content(prompt)
        
        if not response or not response.text:
            logger.error("Received empty response from Gemini")
            return
        
        logger.info(f"Received response from Gemini: {response.text}")
        
        # Parse response
        try:
            # Clean the response text
            cleaned_text = response.text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            cleaned_text = cleaned_text.strip()
            
            logger.info(f"Cleaned response text: {cleaned_text}")
            
            # Try to parse the response as JSON
            specs = json.loads(cleaned_text)
            
            # Validate required fields
            required_fields = ['brand', 'model', 'year', 'fuel_consumption', 'engine_size', 'cylinders', 'transmission', 'fuel_type']
            missing_fields = [field for field in required_fields if field not in specs]
            
            if missing_fields:
                logger.error(f"Missing required fields: {missing_fields}")
                return
            
            # Validate field types
            if not isinstance(specs['brand'], str) or specs['brand'].lower() != brand.lower():
                logger.error(f"Invalid brand value: {specs['brand']}")
                return None
            if not isinstance(specs['model'], str) or specs['model'].lower() != model.lower():
                logger.error(f"Invalid model value: {specs['model']}")
                return None
            if not isinstance(specs['year'], int) or specs['year'] != year:
                logger.error(f"Invalid year value: {specs['year']}")
                return None
            if not isinstance(specs['fuel_consumption'], (int, float)):
                logger.error(f"Invalid fuel_consumption value: {specs['fuel_consumption']}")
                return None
            if not isinstance(specs['engine_size'], int):
                logger.error(f"Invalid engine_size value: {specs['engine_size']}")
                return None
            if not isinstance(specs['cylinders'], int):
                logger.error(f"Invalid cylinders value: {specs['cylinders']}")
                return None
            if not isinstance(specs['transmission'], str):
                logger.error(f"Invalid transmission value: {specs['transmission']}")
                return None
            if not isinstance(specs['fuel_type'], str):
                logger.error(f"Invalid fuel_type value: {specs['fuel_type']}")
                return None
            
            logger.info(f"Successfully parsed vehicle specs: {specs}")
            return specs
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.error(f"Response text: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error getting vehicle specs: {e}")
        return None

if __name__ == "__main__":
    # Test with BMW X6 2020
    test_vehicle_specs("bmw", "x6", 2020) 