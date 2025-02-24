from rest_framework import serializers
from .models import User, UserPreferences, Itinerary, DayPlan, Activity

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'profile_picture', 'is_verified', 'oauth_provider', 'oauth_id')
        extra_kwargs = {
            'password': {'write_only': True},
            'oauth_provider': {'read_only': True},
            'oauth_id': {'read_only': True},
            'is_verified': {'read_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreferences
        fields = ('id', 'user', 'favorite_destinations', 'travel_style', 'dietary_restrictions', 'budget_preference')
        read_only_fields = ('user',)

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'

class DayPlanSerializer(serializers.ModelSerializer):
    activities = ActivitySerializer(many=True, read_only=True)

    class Meta:
        model = DayPlan
        fields = '__all__'

class ItinerarySerializer(serializers.ModelSerializer):
    days = DayPlanSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Itinerary
        fields = ('id', 'user', 'title', 'destination', 'start_date', 'end_date', 'budget', 'status', 'interests', 'days')
        read_only_fields = ('user',)
