import pytest
from unittest.mock import patch, MagicMock
from core.services.itinerary_optimizer import ItineraryOptimizer

@pytest.fixture
def optimizer():
    return ItineraryOptimizer()

def test_optimizer_initialization(optimizer):
    assert isinstance(optimizer, ItineraryOptimizer)
    assert isinstance(optimizer.visited_places, set)
    assert isinstance(optimizer.place_coordinates, dict)
    assert isinstance(optimizer.alternative_places, dict)

def test_get_place_category(optimizer):
    # Test cultural places
    cultural_place = {'name': 'Historical Museum', 'location': 'City Center', 'description': 'A historical museum'}
    assert optimizer.get_place_category(cultural_place) == 'cultural'

    # Test nature places
    nature_place = {'name': 'City Park', 'location': 'Nature Area', 'description': 'Beautiful garden'}
    assert optimizer.get_place_category(nature_place) == 'nature'

    # Test shopping places
    shopping_place = {'name': 'Central Mall', 'location': 'Shopping District', 'description': 'Shopping center'}
    assert optimizer.get_place_category(shopping_place) == 'shopping'

def test_optimize_day_activities(optimizer):
    activities = [
        {
            'name': 'Museum Visit',
            'location': 'City Center',
            'description': 'Historical museum'
        },
        {
            'name': 'Park Walk',
            'location': 'Nature Area',
            'description': 'Beautiful park'
        }
    ]
    visited_places = set()
    
    optimized = optimizer.optimize_day_activities(activities, visited_places)
    assert len(optimized) == 2
    assert all('category' in activity for activity in optimized)

@patch('requests.get')
def test_optimize_day_route(mock_get, optimizer):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{'lat': '48.8584', 'lon': '2.2945'}]
    mock_get.return_value = mock_response

    places = [
        {
            'name': 'Place 1',
            'location': 'Location 1',
            'description': 'Description 1'
        },
        {
            'name': 'Place 2',
            'location': 'Location 2',
            'description': 'Description 2'
        }
    ]
    
    optimized = optimizer.optimize_day_route(places, 'Paris')
    assert isinstance(optimized, list)
    assert len(optimized) == 2

@patch('requests.get')
def test_optimize_itinerary(mock_get, optimizer):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{'lat': '48.8584', 'lon': '2.2945'}]
    mock_get.return_value = mock_response

    itinerary = {
        'day_1': [
            {
                'name': 'Museum Visit',
                'location': 'City Center',
                'description': 'Historical museum'
            },
            {
                'name': 'Park Walk',
                'location': 'Nature Area',
                'description': 'Beautiful park'
            }
        ]
    }
    
    optimized = optimizer.optimize_itinerary(itinerary, 'Paris')
    assert isinstance(optimized, dict)
    assert 'day_1' in optimized
    assert isinstance(optimized['day_1'], list)
    assert len(optimized['day_1']) == 2

def test_haversine_distance(optimizer):
    # Test distance calculation between Paris and London
    paris_lat, paris_lon = 48.8566, 2.3522
    london_lat, london_lon = 51.5074, -0.1278
    
    distance = optimizer.haversine_distance(paris_lat, paris_lon, london_lat, london_lon)
    assert isinstance(distance, float)
    assert 340 <= distance <= 350  # Approximate distance in km

@patch('requests.get')
def test_get_coordinates(mock_get, optimizer):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{'lat': '48.8584', 'lon': '2.2945'}]
    mock_get.return_value = mock_response

    coords = optimizer.get_coordinates('Eiffel Tower', 'Paris')
    assert isinstance(coords, tuple)
    assert len(coords) == 2
    assert all(isinstance(x, float) for x in coords)
