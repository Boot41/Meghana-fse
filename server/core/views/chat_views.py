import json
import uuid
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from ..models import ChatConversation
from ..services.groq_service import GroqService

groq_service = GroqService()

@csrf_exempt
@require_http_methods(["POST"])
def start_chat(request):
    """Start a new chat conversation"""
    session_id = str(uuid.uuid4())
    
    # Get initial greeting from Groq Service
    initial_message = groq_service.generate_travel_suggestions(
        "Give a friendly greeting and ask how you can help with travel planning today.")
    
    # Create new conversation
    conversation = ChatConversation.objects.create(
        session_id=session_id,
        conversation_history=[{
            'role': 'assistant',
            'content': initial_message,
            'timestamp': datetime.now().isoformat()
        }]
    )
    
    return JsonResponse({
        'session_id': session_id,
        'message': initial_message
    })

@csrf_exempt
@require_http_methods(["POST"])
def chat_message(request):
    """Handle chat messages"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        user_message = data.get('message')
        
        if not session_id or not user_message:
            return JsonResponse({
                'error': 'Missing session_id or message'
            }, status=400)
        
        # Get conversation
        try:
            conversation = ChatConversation.objects.get(session_id=session_id)
        except ChatConversation.DoesNotExist:
            return JsonResponse({
                'error': 'Invalid session_id'
            }, status=404)
        
        # Add user message to history
        conversation.conversation_history.append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Process the message with Groq first
        groq_response = groq_service.generate_travel_suggestions(
            user_message,
            conversation.conversation_history
        )
        
        # Try to extract travel parameters
        travel_params = travel_service.extract_travel_params(user_message)
        
        # If we have enough parameters, enhance the response with an itinerary
        if travel_params.get('location') and travel_params.get('duration'):
            try:
                itinerary = travel_service.generate_itinerary(travel_params)
                assistant_message = f"{groq_response}\n\nHere's a suggested itinerary:\n{json.dumps(itinerary, indent=2)}"
            except Exception as e:
                assistant_message = groq_response
        else:
            assistant_message = groq_response
        
        # Add assistant response to history
        conversation.conversation_history.append({
            'role': 'assistant',
            'content': assistant_message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Update conversation stage if needed
        if conversation.stage == 'initial' and travel_params.get('location'):
            conversation.stage = 'planning'
        
        # Save conversation
        conversation.save()
        
        return JsonResponse({
            'message': assistant_message,
            'stage': conversation.stage
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def generate_travel_plan(request):
    """Generate a travel itinerary based on user preferences"""
    try:
        data = json.loads(request.body)
        
        # Generate itinerary using travel service
        itinerary = travel_service.generate_itinerary(data)
        
        # Enhance itinerary with Groq suggestions
        enhanced_itinerary = groq_service.enhance_itinerary(itinerary)
        
        return JsonResponse({
            'itinerary': enhanced_itinerary,
            'message': 'Successfully generated travel plan'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)
