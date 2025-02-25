import json
from django.test import Client
from unittest.mock import patch, MagicMock
import pytest
from core.views.chat_views import start_chat, process_chat, send_itinerary_email
import os

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def mock_smtp():
    with patch('smtplib.SMTP') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        yield mock_server

def test_start_chat_view(client):
    response = client.post('/api/chat/start')
    assert response.status_code == 200
    data = json.loads(response.content)
    assert "Hi! I'm your AI travel assistant." in data['message']
    assert data['currentState']['state'] == 'asking_destination'

def test_start_chat_view_options(client):
    response = client.options('/api/chat/start')
    assert response.status_code == 200

def test_process_chat_view(client):
    with patch('core.services.groq_service.GroqService') as MockGroqService:
        mock_instance = MockGroqService.return_value
        mock_instance.process_message.return_value = {
            'reply': "How many days are you planning to stay? (e.g., '3' for three days)",
            'state': 'asking_duration',
            'preferences': {'destination': 'I want to go to Paris'},
            'data': {}
        }

        data = {
            'message': 'I want to go to Paris',
            'currentState': {'state': 'asking_destination'},
            'preferences': {}
        }
        response = client.post('/api/chat/process', 
                             json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 200
        response_data = json.loads(response.content)
        assert "How many days are you planning to stay?" in response_data['message']
        assert response_data['currentState']['state'] == 'asking_duration'
        assert response_data['preferences'] == {'destination': 'I want to go to Paris'}

def test_process_chat_view_invalid_json(client):
    response = client.post('/api/chat/process', 
                         'invalid json',
                         content_type='application/json')
    assert response.status_code == 500

def test_process_chat_view_options(client):
    response = client.options('/api/chat/process')
    assert response.status_code == 200

def test_send_itinerary_email_success(client, mock_smtp):
    with patch.dict(os.environ, {
        'SMTP_USERNAME': 'test@example.com',
        'SMTP_PASSWORD': 'password'
    }):
        with patch('pdfkit.from_string', return_value=b'pdf content'):
            data = {
                'email': 'test@example.com',
                'itinerary': {
                    'destination': 'Paris',
                    'itinerary': [
                        {
                            'day': 1,
                            'activities': [
                                {
                                    'time': '09:00',
                                    'name': 'Visit Eiffel Tower',
                                    'description': 'Visit the iconic Eiffel Tower'
                                }
                            ]
                        }
                    ]
                }
            }
            response = client.post('/api/chat/send-itinerary',
                                json.dumps(data),
                                content_type='application/json')
            
            assert response.status_code == 200
            response_data = json.loads(response.content)
            assert response_data['message'] == 'Itinerary sent successfully!'

def test_send_itinerary_email_failure(client):
    with patch('core.services.email_service.EmailService') as MockEmailService:
        mock_instance = MockEmailService.return_value
        mock_instance.send_itinerary_email.return_value = False

        data = {
            'email': 'test@example.com',
            'itinerary': {'destination': 'Paris', 'days': [{'activities': []}]}
        }
        response = client.post('/api/chat/send-itinerary',
                             json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 500
        response_data = json.loads(response.content)
        assert response_data['error'] == 'Failed to send email'

def test_send_itinerary_email_missing_data(client):
    data = {'email': 'test@example.com'}  # Missing itinerary
    response = client.post('/api/chat/send-itinerary',
                         json.dumps(data),
                         content_type='application/json')
    
    assert response.status_code == 400
    response_data = json.loads(response.content)
    assert 'error' in response_data

def test_send_itinerary_email_invalid_json(client):
    response = client.post('/api/chat/send-itinerary',
                         'invalid json',
                         content_type='application/json')
    assert response.status_code == 500

def test_send_itinerary_email_options(client):
    response = client.options('/api/chat/send-itinerary')
    assert response.status_code == 200
