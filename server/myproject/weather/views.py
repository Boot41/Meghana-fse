import os
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from core.services.weather_service import WeatherService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize weather service
try:
    weather_service = WeatherService()
    logger.info("✅ WeatherService initialized in weather views")
except Exception as e:
    logger.error(f"❌ Failed to initialize WeatherService: {str(e)}")
    raise

@csrf_exempt
@require_http_methods(["GET"])
def get_weather(request, city):
    """Get weather information for a city"""
    try:
        # Get raw weather data
        weather_data = weather_service.get_weather_info(city)
        
        if weather_data and 'current' in weather_data:
            current = weather_data['current']
            # Return only the data we need
            return JsonResponse({
                'current': {
                    'temp_c': current['temp_c'],
                    'condition': {
                        'text': current['condition']['text'],
                        'icon': current['condition']['icon']
                    },
                    'humidity': current['humidity'],
                    'wind_kph': current['wind_kph'],
                    'wind_dir': current['wind_dir'],
                    'feelslike_c': current['feelslike_c'],
                    'uv': current['uv'],
                    'last_updated': current['last_updated']
                }
            })
        return JsonResponse({'error': 'Weather data not found'}, status=404)
    except Exception as e:
        logger.error(f"Error fetching weather: {str(e)}")  
        return JsonResponse({'error': str(e)}, status=500)
