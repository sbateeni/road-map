from flask import Flask, render_template, request, jsonify
from geocoding_utils import search_cities, get_route_with_traffic
from map_utils import create_map, add_route_with_traffic, save_map
from vehicle_utils import get_vehicle_specs
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search_cities', methods=['GET', 'POST'])
def search_cities_route():
    try:
        # Get query from either GET or POST request
        if request.method == 'GET':
            query = request.args.get('query', '')
        else:
            query = request.json.get('query', '')
            
        if not query:
            return jsonify({'error': 'Query is required'}), 400

        cities = search_cities(query)
        return jsonify({'cities': cities})
    except Exception as e:
        logger.error(f"Error searching cities: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_vehicle_specs', methods=['POST'])
def get_vehicle_specs_route():
    try:
        data = request.json
        brand = data.get('brand')
        model = data.get('model')
        year = data.get('year')

        if not all([brand, model, year]):
            return jsonify({'error': 'Brand, model, and year are required'}), 400

        # Get API key from environment variables
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return jsonify({'error': 'Gemini API key not found'}), 500

        specs = get_vehicle_specs(brand, model, year, api_key)
        if not specs:
            return jsonify({'error': 'Failed to get vehicle specifications'}), 500

        return jsonify({'specs': specs})
    except Exception as e:
        logger.error(f"Error getting vehicle specs: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/calculate_route', methods=['POST'])
def calculate_route():
    try:
        data = request.json
        start_coords = data.get('start')
        end_coords = data.get('end')

        if not start_coords or not end_coords:
            logger.error("Missing start or end coordinates")
            return jsonify({'error': 'Start and end coordinates are required'}), 400

        # Validate coordinates
        try:
            start_lat = float(start_coords.get('latitude', 0))
            start_lon = float(start_coords.get('longitude', 0))
            end_lat = float(end_coords.get('latitude', 0))
            end_lon = float(end_coords.get('longitude', 0))
            
            if not all(isinstance(x, (int, float)) for x in [start_lat, start_lon, end_lat, end_lon]):
                raise ValueError("Invalid coordinate values")
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Invalid coordinates format: {e}")
            return jsonify({'error': 'Invalid coordinates format'}), 400

        # Get route with traffic information
        logger.info(f"Calculating route from ({start_lat}, {start_lon}) to ({end_lat}, {end_lon})")
        route_info = get_route_with_traffic(start_coords, end_coords)
        if not route_info:
            logger.error("Failed to calculate route")
            return jsonify({'error': 'Failed to calculate route'}), 500

        # Create map with route
        try:
            map_obj = create_map(
                (start_lat + end_lat) / 2,
                (start_lon + end_lon) / 2
            )
            add_route_with_traffic(map_obj, start_coords, end_coords)

            # Save map to temporary file
            map_file = 'static/temp_route.html'
            save_map(map_obj, map_file)

            return jsonify({
                'route': route_info,
                'map_url': f'/static/temp_route.html'
            })
        except Exception as e:
            logger.error(f"Error creating map: {e}")
            return jsonify({'error': 'Failed to create map'}), 500

    except Exception as e:
        logger.error(f"Error calculating route: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)
    app.run(debug=True) 