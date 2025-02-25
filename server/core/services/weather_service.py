import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List

class WeatherService:
    def __init__(self):
        self.api_key = os.getenv('WEATHER_API_KEY')
        if not self.api_key:
            raise ValueError("Weather API key not found")
        self.base_url = 'http://api.weatherapi.com/v1'

    def get_forecast(self, city: str, days: int) -> List[Dict]:
        """Get weather forecast for a city for the specified number of days."""
        try:
            url = f"{self.base_url}/forecast.json"
            params = {
                'key': self.api_key,
                'q': city,
                'days': days,
                'aqi': 'no'
            }

            print(f"Fetching weather for {city} for {days} days...")
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if 'forecast' not in data:
                print("No forecast data found")
                return []

            forecast = []
            for day in data['forecast']['forecastday']:
                forecast.append({
                    'day': day['date'],
                    'temp_c': day['day']['avgtemp_c'],
                    'temp_f': day['day']['avgtemp_f'],
                    'condition': day['day']['condition']['text'],
                    'chance_of_rain': day['day']['daily_chance_of_rain']
                })
            return forecast

        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather: {str(e)}")
            return []

    def get_weather_summary(self, forecast: List[Dict]) -> str:
        """Generate a natural language summary of the weather forecast."""
        if not forecast:
            return "Weather information is currently unavailable."

        summary_parts = []
        for day in forecast:
            date = datetime.strptime(day['day'], '%Y-%m-%d').strftime('%A, %B %d')
            summary_parts.append(
                f"{date}: {day['condition']}, "
                f"temperature {day['temp_c']:.0f}°C ({day['temp_f']:.0f}°F)"
            )

        return "Weather forecast: " + ". ".join(summary_parts)

    def get_activity_recommendation(self, weather: Dict) -> str:
        """Get activity recommendations based on weather conditions."""
        condition = weather['condition'].lower()
        temp_c = weather['temp_c']
        chance_of_rain = weather.get('chance_of_rain', 0)

        if 'rain' in condition or 'shower' in condition or chance_of_rain > 60:
            return "indoor"
        elif 'snow' in condition:
            return "snow"
        elif temp_c > 28:
            return "water"
        elif temp_c < 10:
            return "indoor"
        else:
            return "outdoor"

    def get_weather_info(self, city: str) -> Dict:
        """Get current weather information for a city."""
        try:
            url = f"{self.base_url}/current.json"
            params = {
                'key': self.api_key,
                'q': city,
                'aqi': 'no'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            return {
                'location': data['location'],
                'current': data['current']
            }

        except requests.RequestException as e:
            print(f"Error fetching current weather data: {e}")
            return {'error': str(e)}
