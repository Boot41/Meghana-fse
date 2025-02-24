from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from .views import (
    AuthViewSet, UserViewSet, UserPreferencesViewSet,
    TripViewSet, DayPlanViewSet, ActivityViewSet
)

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'users', UserViewSet, basename='user')
router.register(r'preferences', UserPreferencesViewSet, basename='preferences')
router.register(r'trips', TripViewSet, basename='trip')
router.register(r'day-plans', DayPlanViewSet, basename='day-plan')
router.register(r'activities', ActivityViewSet, basename='activity')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
