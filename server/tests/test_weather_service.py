import pytest
from unittest.mock import patch, MagicMock
from core.services.weather_service import WeatherService
import os
import requests

@pytest.fixture
def weather_service():
    with patch.dict(os.environ, {'WEATHER_API_KEY': 'test_key'}):
        return WeatherService()

def test_weather_service_initialization():
    with patch.dict(os.environ, {'WEATHER_API_KEY': 'test_key'}):
        service = WeatherService()
        assert service.api_key == 'test_key'
        assert service.base_url == 'http://api.weatherapi.com/v1'

def test_weather_service_initialization_error():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError):
            WeatherService()

def test_get_forecast_success(weather_service):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'forecast': {
            'forecastday': [
                {
                    'date': '2024-02-25',
                    'day': {
                        'avgtemp_c': 20,
                        'avgtemp_f': 68,
                        'condition': {'text': 'Sunny'},
                        'daily_chance_of_rain': 10
                    }
                }
            ]
        }
    }
    mock_response.status_code = 200

    with patch('requests.get', return_value=mock_response):
        result = weather_service.get_forecast('Paris', 1)
        assert result is not None
        assert len(result) == 1
        assert result[0]['day'] == '2024-02-25'
        assert result[0]['temp_c'] == 20
        assert result[0]['temp_f'] == 68
        assert result[0]['condition'] == 'Sunny'

def test_get_forecast_error(weather_service):
    with patch('requests.get', side_effect=requests.RequestException('API Error')):
        result = weather_service.get_forecast('InvalidCity', 1)
        assert result == []

def test_get_weather_summary_success(weather_service):
    forecast = [{
        'day': '2024-02-25',
        'condition': 'Sunny',
        'temp_c': 20,
        'temp_f': 68,
        'chance_of_rain': 10
    }]
    result = weather_service.get_weather_summary(forecast)
    assert 'Weather forecast' in result
    assert 'Sunny' in result
    assert '20°C' in result

def test_get_weather_summary_empty(weather_service):
    result = weather_service.get_weather_summary([])
    assert result == 'Weather information is currently unavailable.'

def test_get_activity_recommendation_sunny(weather_service):
    weather_data = {
        'condition': 'Sunny',
        'temp_c': 25,
        'chance_of_rain': 0
    }
    result = weather_service.get_activity_recommendation(weather_data)
    assert result == 'outdoor'

def test_get_activity_recommendation_rainy(weather_service):
    weather_data = {
        'condition': 'Rain',
        'temp_c': 20,
        'chance_of_rain': 80
    }
    result = weather_service.get_activity_recommendation(weather_data)
    assert result == 'indoor'

def test_get_weather_info_success(weather_service):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'location': {'name': 'Paris'},
        'current': {'temp_c': 20}
    }
    mock_response.status_code = 200

    with patch('requests.get', return_value=mock_response):
        result = weather_service.get_weather_info('Paris')
        assert result['location']['name'] == 'Paris'
        assert result['current']['temp_c'] == 20

def test_get_weather_info_error(weather_service):
    with patch('requests.get', side_effect=requests.RequestException('API Error')):
        result = weather_service.get_weather_info('InvalidCity')
        assert 'error' in result
