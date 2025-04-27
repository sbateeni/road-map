def calculate_fuel_cost(distance: float, fuel_consumption: float, fuel_price: float) -> dict:
    """Calculate fuel cost for a trip"""
    # Calculate fuel needed (L/100km * distance/100)
    fuel_amount = (fuel_consumption * distance) / 100
    
    # Calculate total cost
    total_cost = fuel_amount * fuel_price
    
    return {
        'fuel_amount': round(fuel_amount, 2),
        'total_cost': round(total_cost, 2)
    }

def extract_fuel_consumption(specs: dict) -> float:
    """Extract fuel consumption from vehicle specifications"""
    try:
        # Try to find fuel consumption in specifications
        if 'specifications' in specs and 'fuel_consumption' in specs['specifications']:
            return float(specs['specifications']['fuel_consumption'])
        else:
            # Default to 8.0 L/100km if not found
            return 8.0
    except (ValueError, TypeError):
        return 8.0 