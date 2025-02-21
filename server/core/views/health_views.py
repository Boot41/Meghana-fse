from django.http import JsonResponse
from core.models import ChatConversation
import uuid

def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({"status": "ok", "message": "Server is running"})

def test_db_connection(request):
    """Test database connection by creating and deleting a record"""
    try:
        # Create a test chat record
        test_record = ChatConversation.objects.create(
            session_id=str(uuid.uuid4()),
            conversation_history=[{"test": "message"}]
        )
        # Delete it right away
        test_record.delete()
        return JsonResponse({
            "status": "ok",
            "message": "Database connection successful"
        })
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)
