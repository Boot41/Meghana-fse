from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import User, UserPreferences, Itinerary, DayPlan, Activity
from .serializers import (
    UserSerializer,
    UserPreferencesSerializer,
    ItinerarySerializer,
    DayPlanSerializer,
    ActivitySerializer
)
from core.services.travel_service import TravelPlannerService
from core.services.weather_service import WeatherService
from core.services.itinerary_optimizer import ItineraryOptimizer

class AuthViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            UserPreferences.objects.create(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        pass  # Implement login logic

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class UserPreferencesViewSet(viewsets.ModelViewSet):
    queryset = UserPreferences.objects.all()
    serializer_class = UserPreferencesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class TripViewSet(viewsets.ModelViewSet):
    serializer_class = ItinerarySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Itinerary.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def generate(self, request):
        try:
            # Initialize services
            travel_service = TravelPlannerService()
            weather_service = WeatherService()
            optimizer = ItineraryOptimizer()

            # Get travel parameters from request
            destination = request.data.get('destination')
            duration = request.data.get('duration')
            budget = request.data.get('budget')
            interests = request.data.get('interests', [])

            # Generate initial travel plan
            travel_plan = travel_service.get_travel_plan(
                destination=destination,
                duration=duration,
                budget=budget,
                interests=interests
            )

            # Get weather data
            weather_data = weather_service.get_weather_forecast(destination)

            # Optimize itinerary
            optimized_plan = optimizer.optimize_itinerary(travel_plan, destination)

            # Create itinerary in database
            itinerary_data = {
                'destination': destination,
                'start_date': request.data.get('start_date'),
                'end_date': request.data.get('end_date'),
                'budget': budget,
                'interests': interests
            }
            serializer = self.get_serializer(data=itinerary_data)
            serializer.is_valid(raise_exception=True)
            itinerary = serializer.save(user=self.request.user)

            # Create day plans and activities
            for day_num, day_plan in enumerate(optimized_plan, 1):
                day_weather = weather_data[day_num - 1] if weather_data else {}
                day = DayPlan.objects.create(
                    itinerary=itinerary,
                    day_number=day_num,
                    weather=day_weather
                )

                for activity in day_plan['activities']:
                    Activity.objects.create(
                        day_plan=day,
                        name=activity['activity'],
                        location=activity.get('location', ''),
                        time=activity.get('time', ''),
                        price_estimate=activity.get('price', ''),
                        category=activity.get('category', 'general')
                    )

            return Response(ItinerarySerializer(itinerary).data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class DayPlanViewSet(viewsets.ModelViewSet):
    serializer_class = DayPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DayPlan.objects.filter(itinerary__user=self.request.user)

class ActivityViewSet(viewsets.ModelViewSet):
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Activity.objects.filter(day_plan__itinerary__user=self.request.user)
