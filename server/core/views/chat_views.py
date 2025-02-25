from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from ..services.groq_service import GroqService
from ..services.weather_service import WeatherService
from ..services.email_service import EmailService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_cors_headers(response):
    """Add CORS headers to response."""
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type"
    return response

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def start_chat(request):
    """Start a new chat session."""
    if request.method == "OPTIONS":
        response = JsonResponse({})
        return add_cors_headers(response)
        
    try:
        logger.info("\nStarting new chat session")
        
        response = JsonResponse({
            "message": "Hi! I'm your AI travel assistant. Where would you like to go?",
            "currentState": {
                "state": "asking_destination",
                "data": {}
            },
            "preferences": {}
        })
        return add_cors_headers(response)

    except Exception as e:
        logger.error(f"Error starting chat: {str(e)}")
        import traceback
        traceback.print_exc()
        response = JsonResponse({
            "message": "I apologize, but I encountered an error. Please try again.",
            "error": str(e)
        }, status=500)
        return add_cors_headers(response)

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def process_chat(request):
    if request.method == "OPTIONS":
        response = JsonResponse({})
        return add_cors_headers(response)
        
    try:
        data = json.loads(request.body)
        message = data.get('message', '')
        current_preferences = data.get('preferences', {})
        current_state = data.get('currentState', {})
        
        logger.info(f"\nProcessing chat message:")
        logger.info(f"Message: {message}")
        logger.info(f"Current state: {current_state}")
        logger.info(f"Current preferences: {current_preferences}")
        
        # Initialize services
        groq_service = GroqService()
        
        # Set the current state and preferences from the request
        state = current_state.get('state', 'asking_destination')
        groq_service.conversation_state = state
        groq_service.current_preferences = current_preferences or {}
        
        # Process the message
        result = groq_service.process_message(message)
        
        logger.info(f"Processing result: {result}")
        
        response = JsonResponse({
            "message": result["reply"],
            "currentState": {
                "state": result["state"],
                "data": result.get("data", {})
            },
            "preferences": result["preferences"]
        })
        return add_cors_headers(response)

    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        import traceback
        traceback.print_exc()
        response = JsonResponse({
            "message": "I apologize, but I encountered an error. Please try again.",
            "error": str(e)
        }, status=500)
        return add_cors_headers(response)

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def send_itinerary_email(request):
    """Send itinerary as PDF to user's email."""
    if request.method == "OPTIONS":
        response = JsonResponse({})
        return add_cors_headers(response)
        
    try:
        data = json.loads(request.body)
        email = data.get('email')
        itinerary_data = data.get('itinerary')
        
        if not email or not itinerary_data:
            response = JsonResponse({
                'error': 'Email and itinerary data are required'
            }, status=400)
            return add_cors_headers(response)
            
        # Initialize email service
        email_service = EmailService()
        
        # Send email
        success = email_service.send_itinerary_email(email, itinerary_data)
        
        if success:
            response = JsonResponse({
                'message': 'Itinerary sent successfully!'
            })
        else:
            response = JsonResponse({
                'error': 'Failed to send email'
            }, status=500)
            
        return add_cors_headers(response)
            
    except Exception as e:
        logger.error(f"Error in send_itinerary_email: {str(e)}")
        response = JsonResponse({
            'error': 'Internal server error'
        }, status=500)
        return add_cors_headers(response)
