import pytest
from unittest.mock import patch, MagicMock
from core.services.travel_service import TravelPlannerService
import os

@pytest.fixture
def travel_service():
    with patch.dict(os.environ, {'RAPID_API_KEY': 'test_key'}):
        return TravelPlannerService(api_key='test_key')

def test_get_places_success(travel_service):
    # Mock location search response
    mock_location_response = MagicMock()
    mock_location_response.status_code = 200
    mock_location_response.json.return_value = {
        'data': [
            {
                'result_type': 'geos',
                'result_object': {
                    'location_id': '123',
                    'name': 'Paris'
                }
            }
        ]
    }

    # Mock places response
    mock_places_response = MagicMock()
    mock_places_response.status_code = 200
    mock_places_response.json.return_value = {
        'data': [
            {
                'name': 'Test Place',
                'description': 'A test place',
                'rating': 4.5,
                'category': {'key': 'attraction'}
            }
        ]
    }

    with patch('requests.get', side_effect=[mock_location_response, mock_places_response]):
        result = travel_service.get_places('Paris', 'attractions')
        assert result is not None
        assert len(result) == 1
        assert result[0]['name'] == 'Test Place'

def test_get_places_error(travel_service):
    with patch('requests.get', side_effect=Exception('API Error')):
        result = travel_service.get_places('InvalidCity', 'attractions')
        assert result == []

def test_get_attractions_success(travel_service):
    # Mock location search response
    mock_location_response = MagicMock()
    mock_location_response.status_code = 200
    mock_location_response.json.return_value = {
        'data': [
            {
                'result_type': 'geos',
                'result_object': {
                    'location_id': '123',
                    'name': 'Paris'
                }
            }
        ]
    }

    # Mock attractions response
    mock_attractions_response = MagicMock()
    mock_attractions_response.status_code = 200
    mock_attractions_response.json.return_value = {
        'data': [
            {
                'name': 'Test Attraction',
                'description': 'A test attraction',
                'rating': 4.5,
                'category': {'key': 'attraction'}
            }
        ]
    }

    with patch('requests.get', side_effect=[mock_location_response, mock_attractions_response]):
        result = travel_service.get_attractions('Paris')
        assert result is not None
        assert len(result) == 1
        assert result[0]['name'] == 'Test Attraction'

def test_generate_itinerary_success(travel_service):
    # Mock location search response
    mock_location_response = MagicMock()
    mock_location_response.status_code = 200
    mock_location_response.json.return_value = {
        'data': [
            {
                'result_type': 'geos',
                'result_object': {
                    'location_id': '123',
                    'name': 'Paris'
                }
            }
        ]
    }

    # Mock places response
    mock_places_response = MagicMock()
    mock_places_response.status_code = 200
    mock_places_response.json.return_value = {
        'data': [
            {
                'name': 'Test Place',
                'description': 'A test place',
                'rating': 4.5,
                'category': {'key': 'attraction'}
            }
        ]
    }

    with patch('requests.get', side_effect=[mock_location_response, mock_places_response]):
        result = travel_service.generate_itinerary('Paris', 3, 'medium', ['culture'])
        assert result is not None
        assert 'itinerary' in result
