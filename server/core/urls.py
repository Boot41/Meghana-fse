from django.urls import path
from .views import travel_views, chat_views, health_views, weather_views

urlpatterns = [
    # Chat API
    path('api/chat/start', chat_views.start_chat, name='start_chat'),
    path('api/chat/process', chat_views.process_chat, name='process_chat'),
    path('api/chat/send-itinerary', chat_views.send_itinerary_email, name='send_itinerary_email'),
    
    # Travel planning API
    path('api/travel/plan', travel_views.plan_travel, name='plan_travel'),
    
    # Health check API
    path('api/health', health_views.health_check, name='health_check'),
    path('api/health/db', health_views.test_db_connection, name='test_db_connection'),
    
    # Weather API
    path('api/weather/<str:city>', weather_views.get_weather, name='get_weather'),
]
