import pytest
from django.test import Client
from unittest.mock import patch, MagicMock
from core.services.weather_service import WeatherService
import json
import requests

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def mock_response():
    mock = MagicMock()
    mock.json.return_value = {
        'location': {
            'name': 'Paris',
            'region': 'Ile-de-France',
            'country': 'France',
            'lat': 48.87,
            'lon': 2.33,
            'localtime': '2024-02-25 10:00'
        },
        'current': {
            'temp_c': 25,
            'condition': {
                'text': 'Sunny',
                'icon': 'sun.png'
            },
            'humidity': 65,
            'wind_kph': 15,
            'wind_dir': 'N',
            'feelslike_c': 26,
            'uv': 6,
            'last_updated': '2024-02-25 10:00'
        }
    }
    mock.status_code = 200
    return mock

def test_weather_service_get_info(mock_response):
    """Test weather service get_weather_info method"""
    with patch('requests.get', return_value=mock_response):
        service = WeatherService()
        weather_data = service.get_weather_info('Paris')
        
        assert weather_data['current']['temp_c'] == 25
        assert weather_data['current']['condition']['text'] == 'Sunny'
        assert weather_data['location']['name'] == 'Paris'

def test_weather_service_get_info_failure():
    """Test weather service failure handling"""
    mock_error_response = MagicMock()
    mock_error_response.status_code = 404
    mock_error_response.raise_for_status.side_effect = requests.exceptions.HTTPError('City not found')
    
    with patch('requests.get', return_value=mock_error_response):
        service = WeatherService()
        weather_data = service.get_weather_info('NonexistentCity')
        assert weather_data == {'error': 'City not found'}

def test_weather_service_get_info_error():
    """Test weather service error handling"""
    with patch('requests.get', side_effect=requests.exceptions.RequestException('API Error')):
        service = WeatherService()
        weather_data = service.get_weather_info('Paris')
        assert weather_data == {'error': 'API Error'}

def test_weather_service_partial_data():
    """Test handling of partial weather data"""
    mock_partial_response = MagicMock()
    mock_partial_response.status_code = 200
    mock_partial_response.json.return_value = {
        'location': {
            'name': 'Paris'
        },
        'current': {
            'temp_c': 25,
            'condition': {
                'text': 'Sunny'
                # Missing icon
            },
            'humidity': 65
            # Missing other fields
        }
    }
    
    with patch('requests.get', return_value=mock_partial_response):
        service = WeatherService()
        weather_data = service.get_weather_info('Paris')
        
        assert weather_data['current']['temp_c'] == 25
        assert weather_data['current']['condition']['text'] == 'Sunny'
        assert 'icon' not in weather_data['current']['condition']
        assert weather_data['location']['name'] == 'Paris'

def test_weather_service_empty_response():
    """Test handling of empty response data"""
    mock_empty_response = MagicMock()
    mock_empty_response.status_code = 200
    mock_empty_response.json.return_value = {
        'location': {
            'name': 'Paris'
        },
        'current': {}
    }
    
    with patch('requests.get', return_value=mock_empty_response):
        service = WeatherService()
        weather_data = service.get_weather_info('Paris')
        assert 'location' in weather_data
        assert 'current' in weather_data
        assert weather_data['location']['name'] == 'Paris'

def test_weather_service_api_error_handling():
    """Test API error handling"""
    mock_timeout = MagicMock()
    mock_timeout.raise_for_status.side_effect = requests.exceptions.RequestException('API timeout')
    
    mock_success = MagicMock()
    mock_success.status_code = 200
    mock_success.json.return_value = {
        'location': {
            'name': 'Paris'
        },
        'current': {'temp_c': 25}
    }
    
    with patch('requests.get', side_effect=[mock_timeout, mock_success]):
        service = WeatherService()
        # First call should return error due to timeout
        weather_data = service.get_weather_info('Paris')
        assert weather_data == {'error': 'API timeout'}
        
        # Second call should succeed
        weather_data = service.get_weather_info('Paris')
        assert weather_data['current']['temp_c'] == 25

def test_get_weather_success(client):
    """Test successful weather data retrieval"""
    mock_weather_data = {
        'location': {
            'name': 'Paris',
            'region': 'Ile-de-France',
            'country': 'France',
            'lat': 48.87,
            'lon': 2.33,
            'localtime': '2024-02-25 10:00'
        },
        'current': {
            'temp_c': 25,
            'condition': {
                'text': 'Sunny',
                'icon': 'sun.png'
            },
            'humidity': 65,
            'wind_kph': 15,
            'wind_dir': 'N',
            'feelslike_c': 26,
            'uv': 6,
            'last_updated': '2024-02-25 10:00'
        }
    }

    with patch.object(WeatherService, 'get_weather_info', return_value=mock_weather_data):
        response = client.get('/api/weather/Paris')
        assert response.status_code == 200
        data = json.loads(response.content)
        
        # Check current weather
        assert data['current']['temp_c'] == 25
        assert data['current']['condition']['text'] == 'Sunny'
        assert data['current']['humidity'] == 65
        assert data['current']['wind_kph'] == 15
        assert data['current']['wind_dir'] == 'N'
        assert data['current']['feelslike_c'] == 26
        assert data['current']['uv'] == 6

def test_get_weather_service_failure(client):
    """Test handling of weather service failure"""
    with patch.object(WeatherService, 'get_weather_info', return_value=None):
        response = client.get('/api/weather/NonexistentCity')
        assert response.status_code == 503
        data = json.loads(response.content)
        assert 'error' in data
        assert 'Failed to fetch weather data' in data['error']

def test_get_weather_service_error(client):
    """Test handling of weather service error"""
    with patch.object(WeatherService, 'get_weather_info', side_effect=Exception('API Error')):
        response = client.get('/api/weather/Paris')
        assert response.status_code == 500
        data = json.loads(response.content)
        assert 'error' in data
        assert 'unexpected error' in data['error'].lower()

def test_get_weather_options_request(client):
    """Test OPTIONS request handling"""
    response = client.options('/api/weather/Paris')
    assert response.status_code == 200
    assert response['Access-Control-Allow-Origin'] == '*'
    assert response['Access-Control-Allow-Methods'] == 'GET, OPTIONS'
    assert response['Access-Control-Allow-Headers'] == 'Content-Type'

def test_get_weather_partial_data(client):
    """Test handling of partial weather data"""
    mock_weather_data = {
        'current': {
            'temp_c': 25,
            'condition': {
                'text': 'Sunny'
                # Missing icon
            },
            'humidity': 65
            # Missing other fields
        }
    }

    with patch.object(WeatherService, 'get_weather_info', return_value=mock_weather_data):
        response = client.get('/api/weather/Paris')
        assert response.status_code == 200
        data = json.loads(response.content)
        
        # Check that missing fields are handled gracefully
        assert data['current']['temp_c'] == 25
        assert data['current']['condition']['text'] == 'Sunny'
        assert data['current']['condition']['icon'] == ''
        assert data['current']['humidity'] == 65

def test_get_weather_empty_response(client):
    """Test handling of empty response data"""
    mock_weather_data = {
        'current': {}
    }

    with patch.object(WeatherService, 'get_weather_info', return_value=mock_weather_data):
        response = client.get('/api/weather/Paris')
        assert response.status_code == 200
        data = json.loads(response.content)
        assert 'current' in data
        assert data['current']['condition']['text'] == ''
        assert data['current']['condition']['icon'] == ''
        assert data['current']['humidity'] is None
