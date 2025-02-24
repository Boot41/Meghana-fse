from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import logging
import json
from ..services.weather_service import WeatherService

logger = logging.getLogger(__name__)

# Create a single instance of WeatherService to use caching
weather_service = WeatherService()

@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def get_weather(request, city):
    """Get weather data for a specific city."""
    
    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        response = JsonResponse({})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response
        
    try:
        logger.info(f"🌤 Getting weather data for {city}")
        
        # Get weather data
        weather_data = weather_service.get_weather_info(city)
        
        if weather_data is None:
            logger.error("❌ Failed to fetch weather data")
            response = JsonResponse({
                "error": "Failed to fetch weather data. Please try again later."
            }, status=503)
            response["Access-Control-Allow-Origin"] = "*"
            return response
            
        # Format the response
        current = weather_data.get('current', {})
        condition = current.get('condition', {})
        
        formatted_data = {
            "current": {
                "temp_c": current.get('temp_c'),
                "condition": {
                    "text": condition.get('text', ''),
                    "icon": condition.get('icon', '')
                },
                "humidity": current.get('humidity'),
                "wind_kph": current.get('wind_kph'),
                "wind_dir": current.get('wind_dir'),
                "feelslike_c": current.get('feelslike_c'),
                "uv": current.get('uv'),
                "last_updated": current.get('last_updated')
            }
        }
        
        # Add forecast data if available
        if 'forecast' in weather_data:
            forecast = weather_data['forecast'].get('forecastday', [])
            formatted_data['forecast'] = [{
                'date': day['date'],
                'max_temp_c': day['day']['maxtemp_c'],
                'min_temp_c': day['day']['mintemp_c'],
                'condition': day['day']['condition'],
                'chance_of_rain': day['day']['daily_chance_of_rain']
            } for day in forecast]
        
        logger.info("✅ Successfully formatted weather data")
        
        # Return response with CORS headers
        response = JsonResponse(formatted_data)
        response["Access-Control-Allow-Origin"] = "*"
        return response
        
    except Exception as e:
        logger.error(f"❌ Error in get_weather view: {str(e)}")
        response = JsonResponse({
            "error": "An unexpected error occurred. Please try again later."
        }, status=500)
        response["Access-Control-Allow-Origin"] = "*"
        return response
