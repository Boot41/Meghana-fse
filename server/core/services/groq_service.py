import os
import requests
from datetime import datetime
from typing import Dict, List, Optional
from groq import Groq
from .weather_service import WeatherService
from .travel_service import TravelPlannerService
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GroqService:
    def __init__(self):
        # Initialize API clients
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.weather_service = WeatherService()
        self.travel_service = TravelPlannerService(os.getenv('RAPID_API_KEY'))  # Fix the environment variable name
        
        # Initialize conversation state
        self.conversation_state = "asking_destination"
        self.conversation_history = []
        self.current_preferences = {}

    def generate_itinerary(self, preferences: Dict) -> Dict:
        """Generate a detailed itinerary using all available services."""
        try:
            destination = preferences.get('destination')
            days = int(preferences.get('days', 3))
            interests = preferences.get('interests', [])
            budget = preferences.get('budget', 'moderate')

            # Get weather forecast
            logger.info(f"Fetching weather for {destination}")
            weather_data = self.weather_service.get_forecast(destination, days)

            # Get travel recommendations
            logger.info(f"Fetching travel recommendations for {destination}")
            attractions = self.travel_service.get_attractions(destination)
            restaurants = self.travel_service.get_restaurants(destination)

            # Prepare context for Groq
            context = {
                "destination": destination,
                "days": days,
                "interests": interests,
                "budget": budget,
                "weather": weather_data,
                "attractions": attractions[:5],  # Top 5 attractions
                "restaurants": restaurants[:5],  # Top 5 restaurants
            }

            # Generate itinerary using Groq
            prompt = self._create_itinerary_prompt(context)
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a travel planning assistant that creates detailed, personalized itineraries."},
                    {"role": "user", "content": prompt}
                ],
                model="mixtral-8x7b-32768",
                temperature=0.7,
                max_tokens=2000
            )

            # Parse and format the response
            itinerary = response.choices[0].message.content
            return {
                "itinerary": itinerary,
                "weather_data": weather_data,
                "attractions": attractions,
                "restaurants": restaurants
            }

        except Exception as e:
            logger.error(f"Error generating itinerary: {str(e)}")
            raise

    def _create_itinerary_prompt(self, context: Dict) -> str:
        """Create a detailed prompt for Groq using all available data."""
        weather_info = "\n".join([
            f"Day {w['day']}: {w['condition']}, {w['temp_c']}°C ({w['temp_f']}°F), {w['chance_of_rain']}% chance of rain"
            for w in context['weather']
        ])

        attractions_info = "\n".join([
            f"- {a['name']}: {a['description'][:100]}..."
            for a in context['attractions']
        ])

        restaurants_info = "\n".join([
            f"- {r['name']}: {r['cuisine']}, {r['price_level']}"
            for r in context['restaurants']
        ])

        return f"""
Create a detailed {context['days']}-day itinerary for {context['destination']} with the following information:

PREFERENCES:
- Duration: {context['days']} days
- Interests: {', '.join(context['interests'])}
- Budget Level: {context['budget']}

WEATHER FORECAST:
{weather_info}

TOP ATTRACTIONS:
{attractions_info}

RECOMMENDED RESTAURANTS:
{restaurants_info}

Please create a day-by-day itinerary that:
1. Considers the weather forecast for outdoor activities
2. Matches the budget level ({context['budget']})
3. Focuses on the specified interests
4. Includes specific restaurants for meals
5. Provides timing for each activity
6. Suggests appropriate clothing/gear based on weather
7. Includes travel tips and recommendations

Format the response as a clear, easy-to-read itinerary with daily schedules.
"""

    def process_message(self, message: str) -> Dict:
        """Process a user message and return the appropriate response."""
        try:
            # Update preferences based on message
            self.current_preferences = self._update_preferences(message)
            
            # Check if we have all required information
            if self._has_all_required_info():
                # Generate itinerary
                itinerary_data = self.generate_itinerary(self.current_preferences)
                self.conversation_state = "complete"
                return {
                    "reply": itinerary_data["itinerary"],
                    "state": self.conversation_state,
                    "data": itinerary_data
                }
            else:
                # Get next question
                next_question = self._get_next_question()
                return {
                    "reply": next_question,
                    "state": self.conversation_state,
                    "data": {}
                }

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "reply": "I apologize, but I encountered an error. Please try again.",
                "state": "error",
                "data": {}
            }

    def _update_preferences(self, message: str) -> Dict:
        """Update preferences based on user message and current state."""
        preferences = self.current_preferences.copy()
        
        if self.conversation_state == "asking_destination":
            preferences["destination"] = message.strip()
            self.conversation_state = "asking_duration"
        
        elif self.conversation_state == "asking_duration":
            try:
                days = int(''.join(filter(str.isdigit, message)))
                preferences["days"] = days
                self.conversation_state = "asking_interests"
            except ValueError:
                preferences["days"] = 3  # Default to 3 days
                
        elif self.conversation_state == "asking_interests":
            interests = [interest.strip().lower() for interest in message.split(',')]
            preferences["interests"] = interests
            self.conversation_state = "asking_budget"
            
        elif self.conversation_state == "asking_budget":
            budget = message.strip().lower()
            if budget in ['budget', 'moderate', 'luxury']:
                preferences["budget"] = budget
            else:
                preferences["budget"] = 'moderate'  # Default to moderate
            self.conversation_state = "generating_itinerary"
            
        return preferences

    def _has_all_required_info(self) -> bool:
        """Check if we have all required information to generate an itinerary."""
        required_fields = ['destination', 'days', 'interests', 'budget']
        return all(field in self.current_preferences for field in required_fields)

    def _get_next_question(self) -> str:
        """Get the next question based on current state."""
        questions = {
            "asking_destination": "Where would you like to go?",
            "asking_duration": "How many days are you planning to stay? (e.g., '3' for three days)",
            "asking_interests": "What are your interests? For example: food, culture, nature, shopping (separate by commas)",
            "asking_budget": "What's your budget level? (budget/moderate/luxury)",
            "generating_itinerary": "Great! Let me create your personalized itinerary..."
        }
        return questions.get(self.conversation_state, "What else would you like to know?")
