from flask import Blueprint, request, jsonify
import logging
from app.services.vehicle_service import VehicleService
from app.services.route_service import RouteService
from app.services.city_service import CityService
from app.config.config import DEFAULT_FUEL_PRICE

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create blueprints
api = Blueprint('api', __name__)
vehicle_service = VehicleService()
route_service = RouteService()
city_service = CityService()

@api.route('/search_cities', methods=['GET'])
def search_cities():
    try:
        query = request.args.get('query', '')
        if not query:
            return jsonify({'results': []})
            
        results = city_service.search_cities(query)
        return jsonify({'results': results})
        
    except Exception as e:
        logger.error(f"Error searching cities: {e}")
        return jsonify({'error': 'حدث خطأ أثناء البحث عن المدن'})

@api.route('/get_vehicle_specs', methods=['POST'])
def get_vehicle_specs():
    try:
        data = request.get_json()
        brand = data.get('brand')
        model = data.get('model')
        year = data.get('year')
        
        if not all([brand, model, year]):
            return jsonify({'error': 'الرجاء إدخال جميع بيانات المركبة'})
        
        specs = vehicle_service.get_vehicle_specs(brand, model, year)
        if not specs:
            return jsonify({'error': 'لم يتم العثور على مواصفات المركبة'})
            
        return jsonify({'specs': specs.to_dict()})
        
    except Exception as e:
        logger.error(f"Error getting vehicle specs: {e}")
        return jsonify({'error': 'حدث خطأ أثناء جلب مواصفات المركبة'})

@api.route('/calculate_route', methods=['POST'])
def calculate_route():
    try:
        data = request.get_json()
        start_coords = data.get('start')
        end_coords = data.get('end')
        route_type = data.get('route_type', 'fastest')
        
        if not all([start_coords, end_coords]):
            return jsonify({'error': 'الرجاء إدخال نقاط البداية والنهاية'})
            
        # Get route information
        route_info = route_service.get_route(start_coords, end_coords, route_type)
        if not route_info:
            return jsonify({'error': 'لم يتم العثور على مسار'})
            
        # Calculate fuel cost if vehicle specs are provided
        if 'vehicle_specs' in data:
            fuel_cost = vehicle_service.calculate_fuel_cost(
                route_info['distance'],
                data['vehicle_specs']['fuel_consumption'],
                DEFAULT_FUEL_PRICE
            )
            if fuel_cost:
                route_info['fuel_cost'] = fuel_cost
                
        return jsonify(route_info)
        
    except Exception as e:
        logger.error(f"Error calculating route: {e}")
        return jsonify({'error': 'حدث خطأ أثناء حساب المسار'}) 