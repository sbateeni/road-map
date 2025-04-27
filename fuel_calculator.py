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

def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
    """Convert amount from one currency to another"""
    # This is a placeholder. In a real application, you would use an API to get exchange rates
    # For now, we'll use some hardcoded rates
    rates = {
        'SAR': 1.0,  # Saudi Riyal
        'USD': 0.27,  # US Dollar
        'EUR': 0.25,  # Euro
        'GBP': 0.21,  # British Pound
        'AED': 0.98,  # UAE Dirham
        'KWD': 0.082,  # Kuwaiti Dinar
        'BHD': 0.10,  # Bahraini Dinar
        'QAR': 0.98,  # Qatari Riyal
        'OMR': 0.10,  # Omani Rial
        'ILS': 1.0,   # Israeli Shekel (نسبة إلى الريال السعودي)
    }
    
    # Convert to USD first
    usd_amount = amount * rates.get(from_currency, 1.0)
    
    # Convert from USD to target currency
    return usd_amount / rates.get(to_currency, 1.0) 