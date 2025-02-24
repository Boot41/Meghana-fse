from django.urls import path
from .views import travel_views
from . import chat_views

urlpatterns = [
    # Chat API
    path('api/chat/', chat_views.chat, name='chat'),
    
    # Travel planning API
    path('api/travel/plan/', travel_views.plan_travel, name='plan_travel'),
]
