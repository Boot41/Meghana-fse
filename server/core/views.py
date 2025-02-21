from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import TestModel

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    return JsonResponse({"status": "ok", "message": "Server is running"})

@csrf_exempt
@require_http_methods(["GET"])
def test_db_connection(request):
    try:
        # Try to create and then delete a test record
        test_record = TestModel.objects.create(name="test")
        test_record.delete()
        return JsonResponse({
            "status": "ok",
            "message": "Database connection successful"
        })
    except Exception as e:
        error_message = str(e)
        print(f"Database error: {error_message}")  # Log the error
        return JsonResponse({
            "status": "error",
            "message": error_message
        }, status=500)
