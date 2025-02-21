from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from ..services.travel_service import TravelPlannerService

@csrf_exempt
@require_http_methods(["POST"])
def plan_travel(request):
    """Handle travel planning requests"""
    try:
        # Parse request body
        data = json.loads(request.body)
        print(f"Received travel request: {data}")
        
        # Initialize service
        service = TravelPlannerService()
        
        # Generate itinerary
        result = service.generate_itinerary(data)
        
        # Check for errors
        if "error" in result:
            return JsonResponse({"error": result["error"]}, status=400)
            
        return JsonResponse(result)
        
    except json.JSONDecodeError as e:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        print(f"Error in plan_travel: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)
