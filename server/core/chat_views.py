import os
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from groq import Groq
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    logger.error("GROQ_API_KEY not found in environment variables")
    raise ValueError("GROQ_API_KEY not found in environment variables")

SYSTEM_PROMPT = """You are a helpful travel assistant. Follow these rules:
1. First ask the user where they would like to go
2. Then ask how many days they plan to stay
3. Then ask about their interests (e.g., food, culture, nature, shopping)
4. Finally ask about their budget level (budget/moderate/luxury)
5. Once you have all the information, create a detailed day-by-day itinerary
6. If any error occurs, apologize and ask the user to try again
7. Keep your responses friendly but concise"""

@csrf_exempt
@require_http_methods(["POST"])
def start_chat(request):
    """Initialize a new chat session"""
    try:
        logger.info("Starting new chat session")
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "assistant", "content": "Hi! I'm your AI travel assistant. Where would you like to go?"}
            ],
            model="mixtral-8x7b-32768",
            temperature=0.7,
            max_tokens=200
        )
        logger.info("Chat session started successfully")
        return JsonResponse({
            "reply": response.choices[0].message.content,
            "state": "asking_destination"
        })
    except Exception as e:
        logger.error(f"Error starting chat: {str(e)}", exc_info=True)
        return JsonResponse({
            "error": "An error occurred while starting the chat",
            "reply": "I apologize, but I encountered an error. Please try refreshing the page.",
            "state": "error"
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def process_chat(request):
    """Process each chat message and maintain conversation state"""
    try:
        data = json.loads(request.body)
        user_message = data.get("message", "")
        current_state = data.get("state", "")
        conversation_history = data.get("history", [])

        logger.info(f"Processing message in state: {current_state}")

        if not user_message:
            return JsonResponse({"error": "Message is required"}, status=400)

        # Build conversation history for context
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in conversation_history:
            messages.append({
                "role": "user" if msg["type"] == "user" else "assistant",
                "content": msg["content"]
            })
        messages.append({"role": "user", "content": user_message})

        # Initialize Groq client
        client = Groq(api_key=GROQ_API_KEY)

        # Add state-specific instructions
        if current_state == "asking_destination":
            messages.append({"role": "system", "content": "Ask about the duration of stay"})
            next_state = "asking_duration"
        elif current_state == "asking_duration":
            messages.append({"role": "system", "content": "Ask about their interests"})
            next_state = "asking_interests"
        elif current_state == "asking_interests":
            messages.append({"role": "system", "content": "Ask about their budget level"})
            next_state = "asking_budget"
        elif current_state == "asking_budget":
            messages.append({"role": "system", "content": "Generate a detailed day-by-day itinerary based on all the information provided"})
            next_state = "generating_itinerary"
        else:
            next_state = "complete"

        # Get response from Groq
        response = client.chat.completions.create(
            messages=messages,
            model="mixtral-8x7b-32768",
            temperature=0.7,
            max_tokens=1000 if next_state == "generating_itinerary" else 200
        )

        logger.info(f"Successfully processed message, next state: {next_state}")
        return JsonResponse({
            "reply": response.choices[0].message.content,
            "state": next_state
        })

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in request: {str(e)}")
        return JsonResponse({
            "error": "Invalid request format",
            "reply": "I apologize, but I couldn't understand your request. Please try again.",
            "state": current_state
        }, status=400)
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        return JsonResponse({
            "error": "An error occurred while processing your message",
            "reply": "I apologize, but I encountered an error while processing your request. Please try again.",
            "state": current_state
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def send_itinerary_email(request):
    """Send the generated itinerary via email"""
    try:
        data = json.loads(request.body)
        email = data.get("email", "")
        itinerary = data.get("itinerary", "")
        
        if not email or not itinerary:
            return JsonResponse({"error": "Email and itinerary are required"}, status=400)
            
        # TODO: Implement email sending functionality
        return JsonResponse({"message": "Email sent successfully"})
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}", exc_info=True)
        return JsonResponse({"error": str(e)}, status=500)
