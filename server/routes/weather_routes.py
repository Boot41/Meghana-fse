from flask import Blueprint, jsonify
from core.services.weather_service import WeatherService
import os

weather_bp = Blueprint('weather', __name__)
weather_service = WeatherService(api_key=os.getenv('WEATHER_API_KEY'))

@weather_bp.route('/<city>')
def get_weather(city):
    """Get weather information for a city"""
    try:
        weather_data = weather_service.get_weather_info(city)
        if weather_data:
            formatted_data = weather_service.format_weather_info(weather_data)
            return jsonify(formatted_data)
        return jsonify({'error': 'Weather data not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
