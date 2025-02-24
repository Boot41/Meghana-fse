from django.urls import path
from .views import travel_views
from . import chat_views

urlpatterns = [
    # Chat API
    path('api/chat/start/', chat_views.start_chat, name='start_chat'),
    path('api/chat/process/', chat_views.process_chat, name='process_chat'),
    path('api/chat/send-email/', chat_views.send_itinerary_email, name='send_itinerary_email'),

    # Travel planning API
    path('api/travel/plan/', travel_views.plan_travel, name='plan_travel'),
]
