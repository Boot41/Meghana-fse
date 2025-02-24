from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from ..services.travel_service import TravelPlannerService

@csrf_exempt
@require_http_methods(["GET", "POST"])
def plan_travel(request):
    """Handle travel planning requests"""
    try:
        if request.method == "GET":
            destination = request.GET.get("destination", "")
            days = int(request.GET.get("days", 5))  # Default to 5 days

            if not destination:
                return JsonResponse({"error": "Destination is required"}, status=400)

            return JsonResponse({"message": f"Generating a {days}-day itinerary for {destination}"})

        # Parse request body for POST requests
        data = json.loads(request.body)
        print(f"Received travel request: {data}")

        destination = data.get("destination", "")
        days = int(data.get("days", 5))  # Default to 5 days

        if not destination:
            return JsonResponse({"error": "Destination is required"}, status=400)

        # Calculate max_tokens based on the trip length
        max_tokens = min(500 + (days * 100), 2000)  # Cap at 2000

        # Initialize travel planner service
        service = TravelPlannerService()

        # Generate itinerary with max_tokens
        result = service.generate_itinerary(data, max_tokens=max_tokens)

        # Check for errors
        if "error" in result:
            return JsonResponse({"error": result["error"]}, status=400)

        return JsonResponse(result)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except ValueError:
        return JsonResponse({"error": "Invalid days value, must be a number"}, status=400)
    except Exception as e:
        print(f"Error in plan_travel: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)
