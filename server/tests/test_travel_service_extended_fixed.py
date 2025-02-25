import pytest
from unittest.mock import patch, MagicMock
from core.services.travel_service import TravelPlannerService
import json
import os

@pytest.fixture
def travel_service():
    with patch.dict(os.environ, {'RAPID_API_KEY': 'test_key'}):
        service = TravelPlannerService(api_key='test_key')
        return service

def test_get_places_with_filters(travel_service):
    """Test getting places with various filters"""
    location_mock = MagicMock()
    location_mock.json.return_value = {
        'data': [{'result_object': {'location_id': '12345'}}]
    }

    places_mock = MagicMock()
    places_mock.json.return_value = {
        'data': [
            {
                'name': 'Eiffel Tower',
                'rating': 4.8,
                'price_level': '$$',
                'description': 'Famous landmark',
                'category': {'key': 'attractions'}
            }
        ]
    }
    
    with patch('requests.get', side_effect=[location_mock, places_mock]):
        places = travel_service.get_places('Paris', 'attractions')
        assert len(places) == 1
        assert places[0]['name'] == 'Eiffel Tower'
        assert places[0]['rating'] == 4.8

def test_get_places_empty_response(travel_service):
    """Test handling of empty response from API"""
    location_mock = MagicMock()
    location_mock.json.return_value = {
        'data': [{'result_object': {'location_id': '12345'}}]
    }

    places_mock = MagicMock()
    places_mock.json.return_value = {'data': []}
    
    with patch('requests.get', side_effect=[location_mock, places_mock]):
        places = travel_service.get_places('NonexistentCity', 'attractions')
        assert len(places) == 0

def test_get_restaurants_with_cuisine(travel_service):
    """Test getting restaurants with cuisine information"""
    with patch('requests.get') as mock_get:
        location_response = MagicMock()
        location_response.json.return_value = {
            'data': [{'result_object': {'location_id': '12345'}}]
        }
        
        restaurant_response = MagicMock()
        restaurant_response.json.return_value = {
            'data': [
                {
                    'name': 'French Bistro',
                    'rating': 4.5,
                    'price_level': '$$',
                    'description': 'Authentic French cuisine',
                    'cuisine': [{'name': 'French'}]
                }
            ]
        }
        mock_get.side_effect = [location_response, restaurant_response]
        
        restaurants = travel_service.get_restaurants('Paris')
        assert len(restaurants) == 1
        assert restaurants[0]['name'] == 'French Bistro'
        assert 'French' in [cuisine['name'] for cuisine in restaurants[0]['cuisine']]

def test_generate_itinerary_with_preferences(travel_service):
    """Test itinerary generation with user preferences"""
    with patch('requests.get') as mock_get:
        location_response = MagicMock()
        location_response.json.return_value = {
            'data': [{'result_object': {'location_id': '12345'}}]
        }
        
        places_response = MagicMock()
        places_response.json.return_value = {
            'data': [
                {
                    'name': 'Cultural Museum',
                    'category': {'key': 'culture'},
                    'rating': 4.5,
                    'description': 'A cultural museum'
                },
                {
                    'name': 'Local Restaurant',
                    'category': {'key': 'food'},
                    'rating': 4.7,
                    'description': 'A local restaurant'
                }
            ]
        }
        mock_get.side_effect = [location_response, places_response]
        
        itinerary = travel_service.generate_itinerary(
            destination='Paris',
            days=2,
            budget=2,
            interests=['culture', 'food']
        )
        assert len(itinerary) == 2

def test_extract_preferences_edge_cases(travel_service):
    """Test edge cases in preference extraction"""
    # Test transport preference with various inputs
    assert travel_service.extract_transport_preference("I prefer public") == "public"
    assert travel_service.extract_transport_preference("private car") == "private"
    assert travel_service.extract_transport_preference("walking tour") == "walking"
    assert travel_service.extract_transport_preference("mixed transport") == "mixed"
    assert travel_service.extract_transport_preference("no preference") is None
    
    # Test activity preference with various inputs
    assert travel_service.extract_activity_preference("I want adventure") == "adventure"
    assert travel_service.extract_activity_preference("something relaxing") == "relaxing"
    assert travel_service.extract_activity_preference("cultural activities") == "cultural"
    assert travel_service.extract_activity_preference("mixed activities") == "mixed"
    assert travel_service.extract_activity_preference("no preference") is None
    
    # Test budget level with various inputs
    assert travel_service.extract_budget_level("Low budget trip") == "low"
    assert travel_service.extract_budget_level("Medium range please") == "medium"
    assert travel_service.extract_budget_level("High end luxury") == "high"
    assert travel_service.extract_budget_level("no preference") is None
    
    # Test duration with various inputs
    assert travel_service.extract_duration("2 days trip") == 2
    assert travel_service.extract_duration("for 5 days please") == 5
    assert travel_service.extract_duration("about 3 days") == 3
    assert travel_service.extract_duration("no duration") is None
    
    # Test food preference with various inputs
    assert travel_service.extract_food_preference("Yes, include food recommendations") is True
    assert travel_service.extract_food_preference("No food needed") is False
    assert travel_service.extract_food_preference("no preference") is None

def test_conversation_state_transitions(travel_service):
    """Test conversation state transitions"""
    # Test initial state
    state = travel_service.determine_conversation_state("Hello", {})
    assert state['state'] == 'START'
    assert "Please enter a valid destination" in state['message']
    
    # Test start state with valid location
    state = travel_service.determine_conversation_state("Paris", {'state': 'START'})
    assert state['state'] == 'DURATION'
    assert state['location'] == 'Paris'
    assert 'message' in state
    
    # Test start state with greeting (should stay in START)
    state = travel_service.determine_conversation_state("hi there", {'state': 'START'})
    assert state['state'] == 'START'
    assert 'message' in state
    
    # Test duration state with valid input
    state = travel_service.determine_conversation_state("3 days", {
        'state': 'DURATION',
        'location': 'Paris'
    })
    assert state['state'] == 'BUDGET'
    assert state['duration'] == 3
    assert 'message' in state
    
    # Test duration state with invalid input
    state = travel_service.determine_conversation_state("too long", {
        'state': 'DURATION',
        'location': 'Paris'
    })
    assert state['state'] == 'DURATION'
    assert 'message' in state
    
    # Test budget state with valid input
    state = travel_service.determine_conversation_state("medium", {
        'state': 'BUDGET',
        'location': 'Paris',
        'duration': 3
    })
    assert state['state'] == 'ACTIVITY'
    assert state['budget'] == 'medium'
    assert 'message' in state
    
    # Test budget state with invalid input
    state = travel_service.determine_conversation_state("super expensive", {
        'state': 'BUDGET',
        'location': 'Paris',
        'duration': 3
    })
    assert state['state'] == 'BUDGET'
    assert 'message' in state
    
    # Test activity state with valid input
    state = travel_service.determine_conversation_state("I want adventure", {
        'state': 'ACTIVITY',
        'location': 'Paris',
        'duration': 3,
        'budget': 'medium'
    })
    assert state['state'] == 'FINAL'
    assert 'activity_type' in state
    assert 'message' in state
