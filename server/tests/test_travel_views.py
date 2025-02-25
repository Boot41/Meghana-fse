import json
import pytest
from django.test import Client
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    return Client()

def test_plan_travel_get_success(client):
    """Test successful GET request for travel planning"""
    response = client.get('/api/travel/plan?destination=Paris&days=3')
    assert response.status_code == 200
    data = response.json()
    assert data['message'] == 'Generating a 3-day itinerary for Paris'

def test_plan_travel_get_missing_destination(client):
    """Test GET request without destination"""
    response = client.get('/api/travel/plan?days=3')
    assert response.status_code == 400
    data = response.json()
    assert data['error'] == 'Destination is required'

def test_plan_travel_get_invalid_days(client):
    """Test GET request with invalid days parameter"""
    response = client.get('/api/travel/plan?destination=Paris&days=invalid')
    assert response.status_code == 400
    data = response.json()
    assert data['error'] == 'Invalid days value, must be a number'

def test_plan_travel_post_success(client):
    """Test successful POST request for travel planning"""
    with patch('core.views.travel_views.TravelPlannerService') as MockService:
        # Create a mock instance with the required api_key parameter
        mock_instance = MagicMock()
        MockService.return_value = mock_instance
        mock_instance.generate_itinerary.return_value = {
            'itinerary': 'Day 1: Visit Eiffel Tower',
            'weather': {'temperature': 20, 'condition': 'Sunny'}
        }

        data = {
            'destination': 'Paris',
            'days': 3,
            'interests': ['culture', 'food']
        }
        response = client.post(
            '/api/travel/plan',
            json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        response_data = response.json()
        assert 'itinerary' in response_data
        assert 'weather' in response_data
        mock_instance.generate_itinerary.assert_called_once()

def test_plan_travel_post_missing_destination(client):
    """Test POST request without destination"""
    data = {
        'days': 3,
        'interests': ['culture', 'food']
    }
    response = client.post(
        '/api/travel/plan',
        json.dumps(data),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = response.json()
    assert data['error'] == 'Destination is required'

def test_plan_travel_post_invalid_json(client):
    """Test POST request with invalid JSON"""
    response = client.post(
        '/api/travel/plan',
        'invalid json',
        content_type='application/json'
    )
    assert response.status_code == 400
    data = response.json()
    assert data['error'] == 'Invalid JSON format'

def test_plan_travel_post_service_error(client):
    """Test POST request when service returns an error"""
    with patch('core.views.travel_views.TravelPlannerService') as MockService:
        # Create a mock instance with the required api_key parameter
        mock_instance = MagicMock()
        MockService.return_value = mock_instance
        mock_instance.generate_itinerary.return_value = {
            'error': 'Service unavailable'
        }

        data = {
            'destination': 'Paris',
            'days': 3
        }
        response = client.post(
            '/api/travel/plan',
            json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data['error'] == 'Service unavailable'
