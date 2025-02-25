import pytest
import os
from unittest.mock import patch, MagicMock
from core.services.groq_service import GroqService

@pytest.fixture
def mock_env():
    with patch.dict(os.environ, {
        'GROQ_API_KEY': 'test_key',
        'WEATHER_API_KEY': 'test_weather_key',
        'RAPID_API_KEY': 'test_rapid_key'
    }):
        yield

@pytest.fixture
def mock_groq_client():
    mock_client = MagicMock()
    mock_chat = MagicMock()
    mock_completions = MagicMock()
    mock_client.chat = mock_chat
    mock_chat.completions = mock_completions
    return mock_client

@pytest.fixture
def groq_service(mock_env, mock_groq_client):
    with patch('core.services.groq_service.Groq') as mock_groq, \
         patch('core.services.groq_service.WeatherService') as mock_weather, \
         patch('core.services.groq_service.TravelPlannerService') as mock_travel:
        mock_groq.return_value = mock_groq_client
        service = GroqService()
        service.client = mock_groq_client
        return service

def test_initialize_client(mock_env, mock_groq_client):
    with patch('core.services.groq_service.Groq') as mock_groq:
        mock_groq.return_value = mock_groq_client
        service = GroqService()
        assert service.client is not None

def test_process_message_initial(groq_service, mock_groq_client):
    # Initial state should be asking_duration
    response = groq_service.process_message("I want to go to Paris")
    assert response["state"] == "asking_duration"
    assert "preferences" in response

def test_process_message_complete(groq_service, mock_groq_client):
    groq_service.current_preferences = {
        "destination": "Paris",
        "days": 3,
        "interests": ["sightseeing"],
        "budget": "moderate"
    }
    groq_service.conversation_state = "complete"
    
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content="Test itinerary"))]
    mock_groq_client.chat.completions.create.return_value = mock_completion
    
    response = groq_service.process_message("Complete")
    assert response["state"] == "complete"
    assert "itinerary" in response["data"]

def test_generate_itinerary_success(groq_service, mock_groq_client):
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content="Test itinerary"))]
    mock_groq_client.chat.completions.create.return_value = mock_completion
    
    preferences = {
        "destination": "Paris",
        "days": 3,
        "interests": ["sightseeing"],
        "budget": "moderate"
    }
    
    with patch.object(groq_service.weather_service, 'get_forecast', return_value=[]), \
         patch.object(groq_service.travel_service, 'get_attractions', return_value=[]), \
         patch.object(groq_service.travel_service, 'get_restaurants', return_value=[]):
        result = groq_service.generate_itinerary(preferences)
        assert "itinerary" in result
        assert result["itinerary"] == "Test itinerary"

def test_generate_itinerary_error(groq_service, mock_groq_client):
    mock_groq_client.chat.completions.create.side_effect = Exception("API Error")
    
    preferences = {
        "destination": "Paris",
        "days": 3,
        "interests": ["sightseeing"],
        "budget": "moderate"
    }
    
    with patch.object(groq_service.weather_service, 'get_forecast', return_value=[]), \
         patch.object(groq_service.travel_service, 'get_attractions', return_value=[]), \
         patch.object(groq_service.travel_service, 'get_restaurants', return_value=[]), \
         pytest.raises(Exception) as exc_info:
        groq_service.generate_itinerary(preferences)
    assert str(exc_info.value) == "API Error"
