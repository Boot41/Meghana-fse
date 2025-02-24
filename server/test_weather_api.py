import requests
import os
from dotenv import load_dotenv
from typing import Dict, Optional

# Load API key from .env
load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

class WeatherService:
    def __init__(self, api_key=None):
        self.api_key = api_key or WEATHER_API_KEY
        if not self.api_key:
            raise ValueError("Weather API key is required")
        self.base_url = "http://api.weatherapi.com/v1"
    
    def get_forecast(self, city: str, days: int = 3) -> Optional[Dict]:
        """Get weather forecast for a city for the next X days."""
        try:
            url = f"{self.base_url}/forecast.json"
            params = {
                'key': self.api_key,
                'q': city,
                'days': days,
                'aqi': 'yes'
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"❌ Weather API error: {str(e)}")
            return None

    def get_weather_info(self, city: str, days: int = 3) -> Optional[Dict]:
        """Get weather information for a city."""
        try:
            forecast = self.get_forecast(city, days)
            if not forecast:
                return None
                
            # Extract relevant weather information
            weather_info = []
            for day in forecast.get('forecast', {}).get('forecastday', []):
                day_info = {
                    'date': day['date'],
                    'condition': day['day']['condition']['text'],
                    'max_temp': day['day']['maxtemp_c'],
                    'min_temp': day['day']['mintemp_c'],
                    'rain_chance': day['day']['daily_chance_of_rain'],
                    'recommendation': self.filter_weather_based_places({
                        'forecast': {'forecastday': [day]}
                    })
                }
                weather_info.append(day_info)
            
            return weather_info
            
        except Exception as e:
            print(f"❌ Weather info error: {str(e)}")
            return None

    def filter_weather_based_places(self, weather_data: Dict) -> str:
        """Suggest places based on weather conditions."""
        if not weather_data or 'forecast' not in weather_data:
            return "⚠ Unable to fetch weather data."

        try:
            forecast_day = weather_data['forecast']['forecastday'][0]
            condition = forecast_day['day']['condition']['text'].lower()
            temp = forecast_day['day']['avgtemp_c']
            rain_chance = forecast_day['day']['daily_chance_of_rain']

            # Basic weather-based recommendations
            if "rain" in condition or rain_chance > 50:
                return "🌧 It's likely to rain. Consider indoor activities like museums, fine dining, or shopping."
            elif "snow" in condition:
                return "❄️ Snow expected! Consider winter sports or cozy indoor cafes."
            elif temp > 30:
                return "🔥 It's hot! Opt for air-conditioned places like malls or evening outdoor activities."
            elif "sunny" in condition:
                return "☀️ Perfect weather for outdoor sightseeing, hiking, or beaches."
            else:
                return "⛅ Moderate weather. You can explore both indoor and outdoor activities."

        except KeyError:
            return "⚠ Could not process weather data."

# Example usage
if __name__ == "__main__":
    city = input("Enter city name: ")
    weather_service = WeatherService()
    weather_data = weather_service.get_forecast(city, days=3)
    
    if weather_data:
        suggestion = weather_service.filter_weather_based_places(weather_data)
        print("\n📌 Travel Recommendation Based on Weather:")
        print(suggestion)
