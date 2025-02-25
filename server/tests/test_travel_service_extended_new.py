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
        mock_response = MagicMock()
        mock_response.json.return_value = {
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
        mock_get.return_value = mock_response
        restaurants = travel_service.get_restaurants('Paris')
        assert len(restaurants) == 1
        assert restaurants[0]['name'] == 'French Bistro'
        assert 'French' in [cuisine['name'] for cuisine in restaurants[0]['cuisine']]

def test_generate_itinerary_with_preferences(travel_service):
    """Test itinerary generation with user preferences"""
    location_mock = MagicMock()
    location_mock.json.return_value = {
        'data': [{'result_object': {'location_id': '12345'}}]
    }

    places_mock = MagicMock()
    places_mock.json.return_value = {
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
    
    with patch('requests.get', side_effect=[location_mock, places_mock]):
        itinerary = travel_service.generate_itinerary(
            destination='Paris',
            days=2,
            budget=2,
            interests=['culture', 'food']
        )
        assert len(itinerary) == 2
        assert any(place['name'] == 'Cultural Museum' for place in itinerary[0])
        assert any(place['name'] == 'Local Restaurant' for place in itinerary[1])

def test_create_day_activities_edge_cases(travel_service):
    """Test edge cases in day activities creation"""
    places = {
        'attractions': [{'name': 'Museum', 'category': {'key': 'museum'}, 'location': {'lat': 0, 'lng': 0}}],
        'restaurants': [{'name': 'Restaurant', 'category': {'key': 'restaurant'}, 'location': {'lat': 0, 'lng': 0}}],
        'nature': [{'name': 'Park', 'category': {'key': 'park'}, 'location': {'lat': 0, 'lng': 0}}],
        'shopping': [{'name': 'Mall', 'category': {'key': 'shopping'}, 'location': {'lat': 0, 'lng': 0}}],
        'entertainment': [{'name': 'Cinema', 'category': {'key': 'entertainment'}, 'location': {'lat': 0, 'lng': 0}}],
        'cultural': [{'name': 'Temple', 'category': {'key': 'temple'}, 'location': {'lat': 0, 'lng': 0}}]
    }
    
    # Test with mixed activity type
    activities = travel_service._create_day_activities(places, "mixed", True)
    assert len(activities) > 0
    
    # Test with bad weather
    weather = {'main': 'Rain', 'description': 'heavy rain'}
    activities = travel_service._create_day_activities(places, "mixed", True, weather)
    assert len(activities) > 0
    
    # Test with good weather
    weather = {'main': 'Clear', 'description': 'clear sky'}
    activities = travel_service._create_day_activities(places, "mixed", True, weather)
    assert len(activities) > 0
    
    # Test without food
    activities = travel_service._create_day_activities(places, "mixed", False)
    assert len(activities) > 0
    assert not any(act['category']['key'] == 'restaurant' for act in activities)
    
    # Test with empty places
    empty_places = {k: [] for k in places.keys()}
    activities = travel_service._create_day_activities(empty_places, "mixed", True)
    assert len(activities) == 0

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
    assert state['state'] == 'TRANSPORT'
    assert state['activity'] == 'adventure'
    assert 'message' in state
    
    # Test activity state with invalid input
    state = travel_service.determine_conversation_state("something invalid", {
        'state': 'ACTIVITY',
        'location': 'Paris',
        'duration': 3,
        'budget': 'medium'
    })
    assert state['state'] == 'ACTIVITY'
    assert 'message' in state
    
    # Test transport state with valid input
    state = travel_service.determine_conversation_state("walking", {
        'state': 'TRANSPORT',
        'location': 'Paris',
        'duration': 3,
        'budget': 'medium',
        'activity': 'adventure'
    })
    assert state['state'] == 'FOOD_PREFERENCE'
    assert state['transport'] == 'walking'
    assert 'message' in state
    
    # Test transport state with invalid input
    state = travel_service.determine_conversation_state("teleport", {
        'state': 'TRANSPORT',
        'location': 'Paris',
        'duration': 3,
        'budget': 'medium',
        'activity': 'adventure'
    })
    assert state['state'] == 'TRANSPORT'
    assert 'message' in state
    
    # Test food preference state with valid input
    state = travel_service.determine_conversation_state("yes include food", {
        'state': 'FOOD_PREFERENCE',
        'location': 'Paris',
        'duration': 3,
        'budget': 'medium',
        'activity': 'adventure',
        'transport': 'walking'
    })
    assert state['state'] == 'FINAL'
    assert state['include_food'] is True
    assert 'message' in state
