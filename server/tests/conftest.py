import os
import django
from django.conf import settings

# Set up test environment variables
os.environ.setdefault('WEATHER_API_KEY', 'test_weather_key')
os.environ.setdefault('GROQ_API_KEY', 'test_groq_key')
os.environ.setdefault('RAPID_API_KEY', 'test_rapid_key')
os.environ.setdefault('EMAIL_HOST', 'localhost')
os.environ.setdefault('EMAIL_PORT', '587')
os.environ.setdefault('EMAIL_HOST_USER', 'test@example.com')
os.environ.setdefault('EMAIL_HOST_PASSWORD', 'test_password')

# Configure Django settings before running tests
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.test_settings')
django.setup()
