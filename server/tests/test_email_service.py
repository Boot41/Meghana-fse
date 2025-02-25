import pytest
import os
from unittest.mock import patch, MagicMock
from core.services.email_service import EmailService

@pytest.fixture
def email_service():
    with patch.dict(os.environ, {
        'SMTP_SERVER': 'smtp.gmail.com',
        'SMTP_PORT': '587',
        'SMTP_USERNAME': 'test@example.com',
        'SMTP_PASSWORD': 'test_password'
    }):
        return EmailService()

def test_email_service_initialization(email_service):
    assert isinstance(email_service, EmailService)
    assert email_service.smtp_server == 'smtp.gmail.com'
    assert email_service.smtp_port == 587
    assert email_service.smtp_username == 'test@example.com'
    assert email_service.smtp_password == 'test_password'

@patch('smtplib.SMTP')
@patch('pdfkit.from_string')
def test_send_itinerary_email(mock_pdfkit, mock_smtp, email_service):
    # Mock PDF generation
    mock_pdf = b'mock_pdf_content'
    mock_pdfkit.return_value = mock_pdf

    # Mock SMTP instance
    mock_smtp_instance = mock_smtp.return_value
    mock_smtp_instance.__enter__.return_value = mock_smtp_instance

    # Test data
    itinerary = {
        'destination': 'Paris',
        'duration': 3,
        'itinerary': [
            {
                'day': 1,
                'weather': {'condition': 'Sunny', 'temperature': 25},
                'activities': [
                    {
                        'time': '09:00',
                        'name': 'Eiffel Tower',
                        'description': 'Visit the iconic tower',
                        'weather_note': 'Perfect weather for sightseeing'
                    }
                ]
            }
        ],
        'tips': ['Bring comfortable shoes']
    }
    recipient_email = 'recipient@example.com'

    # Send email
    result = email_service.send_itinerary_email(recipient_email, itinerary)

    # Verify SMTP interactions
    mock_smtp_instance.starttls.assert_called_once()
    mock_smtp_instance.login.assert_called_once_with(
        email_service.smtp_username,
        email_service.smtp_password
    )
    mock_smtp_instance.send_message.assert_called_once()

    assert result is True

@patch('smtplib.SMTP')
@patch('pdfkit.from_string')
def test_send_itinerary_email_error(mock_pdfkit, mock_smtp, email_service):
    # Mock PDF generation error
    mock_pdfkit.side_effect = Exception("PDF generation failed")

    # Test data
    itinerary = {
        'destination': 'Paris',
        'duration': 3,
        'itinerary': []
    }
    recipient_email = 'recipient@example.com'

    # Send email should handle error gracefully
    result = email_service.send_itinerary_email(recipient_email, itinerary)
    assert result is False
