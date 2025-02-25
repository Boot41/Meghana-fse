import pytest
from unittest.mock import patch, MagicMock
from core.services.travel_service import TravelPlannerService
import os

@pytest.fixture
def travel_service():
    with patch.dict(os.environ, {'RAPID_API_KEY': 'test_key'}):
        return TravelPlannerService(api_key='test_key')

def test_travel_service_initialization(travel_service):
    assert isinstance(travel_service, TravelPlannerService)
    assert travel_service.api_key == 'test_key'
    assert travel_service.base_url == 'https://travel-advisor.p.rapidapi.com'

def test_determine_conversation_state_initial(travel_service):
    state = travel_service.determine_conversation_state("Hello", {})
    assert state['state'] == 'START'
    assert "Please enter a valid destination" in state['message']

def test_determine_conversation_state_duration(travel_service):
    current_state = {'state': 'START'}
    state = travel_service.determine_conversation_state("Paris", current_state)
    assert state['state'] == 'DURATION'
    assert state['location'] == 'Paris'
    assert "How many days" in state['message']

def test_determine_conversation_state_budget(travel_service):
    current_state = {'state': 'DURATION', 'location': 'Paris'}
    state = travel_service.determine_conversation_state("5 days", current_state)
    assert state['state'] == 'BUDGET'
    assert state['duration'] == 5
    assert "budget level" in state['message'].lower()

def test_extract_location(travel_service):
    message = "I want to visit Paris"
    with patch.object(travel_service, 'extract_location', return_value='Paris'):
        location = travel_service.extract_location(message)
        assert location == "Paris"

def test_extract_duration(travel_service):
    duration = travel_service.extract_duration("I want to stay for 5 days")
    assert duration == 5

def test_extract_budget_level(travel_service):
    budget = travel_service.extract_budget_level("I have a medium budget")
    assert budget == "medium"

def test_extract_activity_preference(travel_service):
    message = "I like museums and cultural activities"
    with patch.object(travel_service, 'extract_activity_preference', return_value=['cultural', 'museums']):
        preferences = travel_service.extract_activity_preference(message)
        assert isinstance(preferences, list)
        assert len(preferences) == 2
        assert preferences == ['cultural', 'museums']

@patch('requests.get')
def test_get_places(mock_get, travel_service):
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

    mock_get.side_effect = [mock_location_response, mock_places_response]
    result = travel_service.get_places('Paris', 'attractions')
    assert result is not None
    assert len(result) == 1
    assert result[0]['name'] == 'Test Place'

@patch('requests.get')
def test_get_attractions(mock_get, travel_service):
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

    mock_get.side_effect = [mock_location_response, mock_attractions_response]
    result = travel_service.get_attractions('Paris')
    assert result is not None
    assert len(result) == 1
    assert result[0]['name'] == 'Test Attraction'

@patch('requests.get')
def test_get_restaurants(mock_get, travel_service):
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

    mock_restaurants_response = MagicMock()
    mock_restaurants_response.status_code = 200
    mock_restaurants_response.json.return_value = {
        'data': [
            {
                'name': 'Test Restaurant',
                'description': 'A test restaurant',
                'rating': 4.5,
                'category': {'key': 'restaurant'}
            }
        ]
    }

    mock_get.side_effect = [mock_location_response, mock_restaurants_response]
    result = travel_service.get_restaurants('Paris')
    assert result is not None
    assert len(result) == 1
    assert result[0]['name'] == 'Test Restaurant'

@patch('requests.get')
def test_get_travel_plan(mock_get, travel_service):
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

    mock_get.side_effect = [mock_location_response, mock_places_response]
    result = travel_service.get_travel_plan('Paris', 3, 'medium', ['culture'])
    assert isinstance(result, dict)
    assert 'destination' in result
    assert result['destination'].lower() == 'paris'
    assert 'budget' in result
    assert result['budget'] == 'medium'

@patch('requests.get')
def test_get_location_id(mock_get, travel_service):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
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

    mock_get.return_value = mock_response
    location_id = travel_service._get_location_id('Paris')
    assert location_id == '123'
