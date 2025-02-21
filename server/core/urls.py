from django.urls import path
from .views import health_views, chat_views, travel_views

urlpatterns = [
    # Health check endpoints
    path('health/', health_views.health_check, name='health_check'),
    path('test-db/', health_views.test_db_connection, name='test_db_connection'),
    
    # Chat endpoints
    path('chat/start/', chat_views.start_chat, name='start_chat'),
    path('chat/message/', chat_views.chat_message, name='chat_message'),
    
    # Travel planning endpoints
    path('travel/plan/', travel_views.plan_travel, name='plan_travel'),
]
