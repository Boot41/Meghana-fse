import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from ..services.groq_service import GroqService
from ..services.weather_service import WeatherService
from ..services.email_service import EmailService

@csrf_exempt
@require_http_methods(["POST"])
def start_chat(request):
    """Initialize a new chat session."""
    try:
        # Initialize a new GroqService for this session
        groq_service = GroqService()
        
        return JsonResponse({
            "message": "Hi! I'm your AI travel assistant. Let's plan your perfect trip! Where would you like to go?",
            "currentState": {
                "state": groq_service.conversation_state,
                "data": {}
            }
        })
    except Exception as e:
        print(f"Error starting chat: {str(e)}")
        return JsonResponse({
            "message": "I apologize, but I couldn't start the chat. Please try again.",
            "error": str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def process_chat(request):
    """Process chat messages and generate responses with travel recommendations."""
    try:
        data = json.loads(request.body)
        message = data.get('message', '')
        current_preferences = data.get('preferences', {})
        current_state = data.get('currentState', {})
        
        print(f"\nProcessing chat message:")
        print(f"Message: {message}")
        print(f"Current state: {current_state}")
        print(f"Current preferences: {current_preferences}")
        
        # Initialize services
        groq_service = GroqService()
        weather_service = WeatherService()

        # Extract or update preferences from the message
        result = groq_service.extract_preferences(message, current_preferences)
        
        print(f"Extract preferences result: {result}")
        
        # Ensure we got a valid result
        if not result or not isinstance(result, dict):
            print("Error: Invalid response format")
            return JsonResponse({
                "message": "I apologize, but I couldn't process your message. Please try again.",
                "error": "Invalid response format"
            }, status=400)

        # Get the components from the result
        preferences = result.get('preferences', {})
        message = result.get('message', '')
        current_state = result.get('current_state', '')
        itinerary = result.get('itinerary', [])
        tips = result.get('tips', [])
        weather_summary = result.get('weather_summary', '')

        # Return the response
        response_data = {
            "message": message,
            "preferences": preferences,
            "currentState": {
                "state": current_state,
                "data": preferences
            }
        }

        # Add itinerary data if present
        if itinerary or tips or weather_summary:
            response_data.update({
                "itinerary": itinerary,
                "tips": tips,
                "weather_summary": weather_summary
            })

        return JsonResponse(response_data)

    except json.JSONDecodeError:
        print("Error: Invalid JSON request")
        return JsonResponse({
            "message": "Invalid request format. Please provide valid JSON.",
            "error": "Invalid JSON"
        }, status=400)
    except Exception as e:
        print(f"Error processing chat: {str(e)}")
        return JsonResponse({
            "message": "I apologize, but I encountered an error. Please try again.",
            "error": str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def send_itinerary_email(request):
    """Send itinerary as PDF to user's email."""
    try:
        data = json.loads(request.body)
        email = data.get('email')
        itinerary_data = data.get('itinerary')
        
        if not email or not itinerary_data:
            return JsonResponse({
                'error': 'Email and itinerary data are required'
            }, status=400)
            
        # Initialize email service
        email_service = EmailService()
        
        # Send email
        success = email_service.send_itinerary_email(email, itinerary_data)
        
        if success:
            return JsonResponse({
                'message': 'Itinerary sent successfully!'
            })
        else:
            return JsonResponse({
                'error': 'Failed to send email'
            }, status=500)
            
    except Exception as e:
        print(f"Error in send_itinerary_email: {str(e)}")
        return JsonResponse({
            'error': 'Internal server error'
        }, status=500)
