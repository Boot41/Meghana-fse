from rest_framework import viewsets, permissions
from ..models import Itinerary, DayPlan, Activity
from ..serializers import ItinerarySerializer, DayPlanSerializer, ActivitySerializer

class TripViewSet(viewsets.ModelViewSet):
    queryset = Itinerary.objects.all()
    serializer_class = ItinerarySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class DayPlanViewSet(viewsets.ModelViewSet):
    queryset = DayPlan.objects.all()
    serializer_class = DayPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(itinerary__user=self.request.user)

class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(day_plan__itinerary__user=self.request.user)
