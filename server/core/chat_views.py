import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .services.groq_service import GroqService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
groq_service = None

def initialize_services():
    """Initialize all required services."""
    global groq_service
    try:
        # Check for required API keys
        required_keys = ['GROQ_API_KEY', 'WEATHER_API_KEY', 'RAPID_API_KEY']
        missing_keys = [key for key in required_keys if not os.getenv(key)]
        
        if missing_keys:
            raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")
            
        groq_service = GroqService()
        logger.info("✅ Successfully initialized all services")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error initializing services: {str(e)}")
        return False

# Initialize services when the module loads
initialize_services()

@csrf_exempt
@require_http_methods(["POST"])
def chat(request):
    """Handle chat messages and return appropriate responses."""
    try:
        # Ensure services are initialized
        if not groq_service:
            logger.error("Services not initialized, attempting to initialize...")
            if not initialize_services():
                logger.error("Failed to initialize services")
                return JsonResponse({
                    "error": "Services not properly initialized. Check API keys and try again."
                }, status=500)

        # Parse request data
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        
        if not message:
            logger.warning("Received empty message")
            return JsonResponse({
                "error": "Message cannot be empty"
            }, status=400)

        # Process message and get response
        logger.info(f"Processing message: {message}")
        try:
            response = groq_service.process_message(message)
            logger.info(f"Got response: {response}")
            
            return JsonResponse({
                "reply": response["reply"],
                "state": response["state"],
                "data": response["data"]
            })
            
        except Exception as e:
            logger.error(f"Error in groq_service.process_message: {str(e)}", exc_info=True)
            return JsonResponse({
                "error": "Error processing message",
                "reply": "I apologize, but I encountered an error while processing your request. Please try again.",
                "state": "error",
                "data": {}
            }, status=500)

    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return JsonResponse({
            "error": "Invalid JSON in request body"
        }, status=400)
        
    except Exception as e:
        logger.error(f"Unexpected error in chat view: {str(e)}", exc_info=True)
        return JsonResponse({
            "error": "An unexpected error occurred"
        }, status=500)
