from django.db import models

class TravelItinerary(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    destination = models.CharField(max_length=200)
    duration_days = models.IntegerField()
    interests = models.JSONField(default=list)  # List of interests
    budget = models.CharField(max_length=50)  # low, medium, high
    travel_style = models.CharField(max_length=50)  # relaxed, balanced, active
    itinerary_data = models.JSONField(default=dict)  # The full itinerary

    def __str__(self):
        return f"{self.duration_days}-day trip to {self.destination}"

class ChatConversation(models.Model):
    session_id = models.CharField(max_length=100, unique=True)
    conversation_history = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Chat session {self.session_id}"

    class Meta:
        db_table = 'chat_conversation'
