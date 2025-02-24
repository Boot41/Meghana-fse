import os
import requests
from datetime import datetime
from typing import Dict, List, Optional
from groq import Groq
from .weather_service import WeatherService
import json
import time

class GroqService:
    def __init__(self):
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.weather_service = WeatherService()
        self.conversation_state = "asking_destination"
        self.conversation_history = []

    def _get_next_question(self, current_state: str, preferences: Dict) -> str:
        """Get the next question based on current state and preferences."""
        destination = preferences.get('destination', '')
        if not destination and current_state == "asking_dates":
            # If destination is missing, revert to asking for destination
            return "What city would you like to visit?"
            
        questions = {
            "asking_destination": "What city would you like to visit?",
            "asking_dates": "How many days are you planning to stay? (e.g., '3' for three days)",
            "asking_interests": "What kind of activities interest you? For example: culture, nature, food, shopping, or relaxation?",
            "asking_budget": "What's your budget range for this trip? (budget, moderate, or luxury)",
            "planning": "Great! Let me create your personalized itinerary..."
        }
        return questions.get(current_state, "What else would you like to know?")

    def extract_preferences(self, user_input: str, current_preferences: Dict) -> Dict:
        """Extract travel preferences from user input."""
        try:
            print("\n=== Extracting Preferences ===")
            print(f"Current state: {current_preferences.get('current_state', 'asking_destination')}")
            print(f"User input: {user_input}")
            print(f"Current preferences: {current_preferences}")

            preferences = current_preferences.copy()
            current_state = preferences.get('current_state', 'asking_destination')

            if current_state == 'asking_destination':
                # Extract destination
                destination = user_input.strip()
                if destination:
                    preferences['destination'] = destination
                    preferences['current_state'] = 'asking_dates'
                    return {
                        'preferences': preferences,
                        'message': "How many days are you planning to stay? (e.g., '3' for three days)",
                        'current_state': 'asking_dates'
                    }

            elif current_state == 'asking_dates':
                try:
                    # Clean up input and get number of days
                    days_input = user_input.strip().lower()
                    days_input = ''.join(c for c in days_input if c.isdigit())
                    
                    if not days_input:
                        return {
                            'preferences': preferences,
                            'message': "Please enter a number between 1 and 30 for your stay duration.",
                            'current_state': 'asking_dates'
                        }
                    
                    days = int(days_input)
                    if days < 1 or days > 30:
                        return {
                            'preferences': preferences,
                            'message': "Please enter a number between 1 and 30 for your stay duration.",
                            'current_state': 'asking_dates'
                        }
                    
                    # Get current date for reference
                    from datetime import datetime, timedelta
                    start_date = datetime.now()
                    end_date = start_date + timedelta(days=days-1)
                    
                    # Store the dates and days
                    preferences['start_date'] = start_date.strftime('%Y-%m-%d')
                    preferences['end_date'] = end_date.strftime('%Y-%m-%d')
                    preferences['days'] = days
                    preferences['current_state'] = 'asking_interests'
                    
                    print(f"Processed stay duration: {days} days")
                    print(f"Date range for reference: {preferences['start_date']} to {preferences['end_date']}")
                    
                    return {
                        'preferences': preferences,
                        'message': "What are your interests? For example: food, culture, nature, shopping, etc.",
                        'current_state': 'asking_interests'
                    }
                except ValueError as e:
                    print(f"Error processing days: {str(e)}")
                    return {
                        'preferences': preferences,
                        'message': "Please enter a valid number between 1 and 30 for your stay duration.",
                        'current_state': 'asking_dates'
                    }

            elif current_state == 'asking_interests':
                # Extract interests
                interests = [interest.strip() for interest in user_input.lower().split(',')]
                if interests:
                    preferences['interests'] = interests
                    preferences['current_state'] = 'asking_budget'
                    return {
                        'preferences': preferences,
                        'message': "What's your budget level? (budget/moderate/luxury)",
                        'current_state': 'asking_budget'
                    }

            elif current_state == 'asking_budget':
                # Validate and extract budget
                budget = user_input.lower().strip()
                valid_budgets = {'budget', 'moderate', 'luxury'}
                
                if budget in valid_budgets:
                    preferences['budget'] = budget
                    preferences['current_state'] = 'generating_itinerary'
                    
                    # Generate itinerary
                    itinerary = self.generate_itinerary(preferences)
                    
                    return {
                        'preferences': preferences,
                        'message': itinerary.get('message', ''),
                        'current_state': 'complete',
                        'itinerary': itinerary.get('itinerary', []),
                        'tips': itinerary.get('tips', []),
                        'weather_summary': itinerary.get('weather_summary', '')
                    }
                else:
                    return {
                        'preferences': preferences,
                        'message': "Please choose a valid budget level: budget, moderate, or luxury.",
                        'current_state': 'asking_budget'
                    }

            return {
                'preferences': preferences,
                'message': "I didn't understand that. Could you please try again?",
                'current_state': current_state
            }

        except Exception as e:
            print(f"Error in extract_preferences: {str(e)}")
            return {
                'preferences': current_preferences,
                'message': "I encountered an error. Could you please try again?",
                'current_state': current_preferences.get('current_state', 'asking_destination')
            }

    def _validate_budget(self, budget: str) -> tuple[bool, str]:
        """Validate and normalize budget input."""
        valid_budgets = {
            'budget': ['budget', 'cheap', 'low', 'economical', 'inexpensive'],
            'moderate': ['moderate', 'medium', 'mid', 'average'],
            'luxury': ['luxury', 'luxurious', 'high', 'expensive', 'premium', 'uxury']  # Handle typo
        }
        
        budget = budget.lower().strip()
        for category, keywords in valid_budgets.items():
            if budget in keywords or any(keyword in budget for keyword in keywords):
                return True, category
        return False, ''

    def _suggest_activities(self, weather_condition: str, temperature: float) -> List[str]:
        """Suggest activities based on weather conditions."""
        activities = {
            "sunny_hot": [
                "Visit air-conditioned museums",
                "Indoor shopping malls",
                "Water parks",
                "Beach (early morning or late afternoon)",
                "Indoor cultural experiences",
                "Spa treatments"
            ],
            "sunny_warm": [
                "Beach activities",
                "Outdoor sightseeing",
                "Walking tours",
                "Outdoor dining",
                "Park visits",
                "Boat tours"
            ],
            "rainy": [
                "Museum visits",
                "Indoor markets",
                "Local cooking classes",
                "Theater shows",
                "Indoor attractions",
                "Shopping centers"
            ],
            "cold": [
                "Indoor cultural sites",
                "Cozy cafes",
                "Indoor workshops",
                "Shopping",
                "Museums and galleries",
                "Local food experiences"
            ]
        }

        if "rain" in weather_condition.lower():
            return activities["rainy"]
        elif temperature > 30:
            return activities["sunny_hot"]
        elif temperature > 20:
            return activities["sunny_warm"]
        else:
            return activities["cold"]

    def _format_itinerary_response(self, itinerary_data: Dict, weather_data: List[Dict], preferences: Dict) -> Dict:
        """Format the itinerary response with proper dates and weather-aware activities."""
        try:
            # Start with the base response from the AI
            response = {
                "message": itinerary_data.get('message', f"Here's your personalized itinerary for {preferences['destination']}!"),
                "itinerary": [],
                "tips": itinerary_data.get('tips', [])
            }

            # Create day-by-day itinerary
            for day_weather in weather_data:
                date = day_weather['date']
                condition = day_weather['condition'].lower()
                temp = day_weather['temperature']['avg']
                rain_chance = day_weather['rain_chance']

                # Get weather-appropriate activities
                suggested_activities = self._suggest_activities(condition, temp)
                
                # Find matching day in AI-generated itinerary
                ai_day = next(
                    (day for day in itinerary_data.get('itinerary', []) if day.get('date') == date),
                    None
                )

                # Format the day's plan
                day_plan = {
                    "date": date,
                    "weather": {
                        "condition": day_weather['condition'],
                        "temperature": f"{temp}°C",
                        "rain_chance": f"{rain_chance}%"
                    },
                    "plan": []
                }

                # Merge AI suggestions with weather-appropriate activities
                if temp > 30:  # Hot day
                    time_slots = [
                        {
                            "time": "Early Morning (6:00 AM - 9:00 AM)",
                            "activities": (
                                ai_day.get('morning_activities', []) if ai_day 
                                else ["Outdoor sightseeing while it's cool"] + suggested_activities[:2]
                            )
                        },
                        {
                            "time": "Morning (9:00 AM - 12:00 PM)",
                            "activities": ["Indoor activities due to heat"] + (
                                ai_day.get('late_morning_activities', []) if ai_day
                                else suggested_activities[2:4]
                            )
                        },
                        {
                            "time": "Afternoon (12:00 PM - 4:00 PM)",
                            "activities": ["Indoor activities recommended"] + (
                                ai_day.get('afternoon_activities', []) if ai_day
                                else suggested_activities[4:6]
                            )
                        },
                        {
                            "time": "Evening (4:00 PM - 8:00 PM)",
                            "activities": ai_day.get('evening_activities', []) if ai_day else suggested_activities[6:]
                        }
                    ]
                elif "rain" in condition or rain_chance > 60:  # Rainy day
                    time_slots = [
                        {
                            "time": "Morning (8:00 AM - 12:00 PM)",
                            "activities": (
                                ai_day.get('morning_activities', []) if ai_day
                                else ["Indoor cultural activities"] + suggested_activities[:2]
                            )
                        },
                        {
                            "time": "Afternoon (12:00 PM - 4:00 PM)",
                            "activities": (
                                ai_day.get('afternoon_activities', []) if ai_day
                                else suggested_activities[2:5]
                            )
                        },
                        {
                            "time": "Evening (4:00 PM - 8:00 PM)",
                            "activities": (
                                ai_day.get('evening_activities', []) if ai_day
                                else suggested_activities[5:]
                            )
                        }
                    ]
                else:  # Pleasant weather
                    time_slots = [
                        {
                            "time": "Morning (8:00 AM - 12:00 PM)",
                            "activities": (
                                ai_day.get('morning_activities', []) if ai_day
                                else ["Outdoor exploration"] + suggested_activities[:2]
                            )
                        },
                        {
                            "time": "Afternoon (12:00 PM - 4:00 PM)",
                            "activities": (
                                ai_day.get('afternoon_activities', []) if ai_day
                                else suggested_activities[2:5]
                            )
                        },
                        {
                            "time": "Evening (4:00 PM - 8:00 PM)",
                            "activities": (
                                ai_day.get('evening_activities', []) if ai_day
                                else suggested_activities[5:]
                            )
                        }
                    ]

                day_plan["plan"] = time_slots
                response["itinerary"].append(day_plan)

            # Add weather-specific tips
            weather_conditions = set(day['condition'].lower() for day in weather_data)
            if any('rain' in cond for cond in weather_conditions):
                response["tips"].append("Pack an umbrella or raincoat as there's a chance of rain during your visit.")
            if any(day['temperature']['avg'] > 30 for day in weather_data):
                response["tips"].append("Some days might be quite hot. Plan outdoor activities for early morning or evening.")
            if any(day['temperature']['avg'] < 15 for day in weather_data):
                response["tips"].append("Pack some warm clothes as temperatures might be cool during your visit.")

            # Add interest-based tips
            interests = preferences.get('interests', [])
            if 'food' in interests:
                response["tips"].append("Bangalore is known for its diverse culinary scene. Try local South Indian dishes!")
            if 'culture' in interests:
                response["tips"].append("Visit temples early in the morning for a more peaceful experience.")

            # Add budget-specific tips
            budget = preferences.get('budget')
            if budget == 'luxury':
                response["tips"].extend([
                    "Consider booking luxury spa treatments in advance.",
                    "Many high-end restaurants require reservations.",
                    "Private guided tours are available for most attractions."
                ])
            elif budget == 'budget':
                response["tips"].extend([
                    "Local street food offers great value and authentic flavors.",
                    "Consider using public transportation or ride-sharing services.",
                    "Many temples and parks have free entry."
                ])
            
            return response

        except Exception as e:
            print(f"Error formatting itinerary: {e}")
            return {
                "message": "I apologize, but I couldn't format your itinerary properly. Please try again.",
                "itinerary": [],
                "tips": []
            }

    def _enhance_itinerary_with_groq(self, base_itinerary, weather_data, preferences):
        """Enhance the itinerary using Groq's LLM capabilities with retry logic."""
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                # Format weather data for the prompt
                weather_summary = []
                for day in weather_data:
                    weather_summary.append(
                        f"Day {day['day']}: {day['condition']}, "
                        f"Temperature: {day['temp_c']}°C ({day['temp_f']}°F), "
                        f"Chance of rain: {day['chance_of_rain']}%"
                    )
                
                # Create the prompt
                prompt = f"""You are a travel expert. Enhance this itinerary for {preferences['destination']} 
                considering the following weather conditions:
                {chr(10).join(weather_summary)}
                
                Base itinerary:
                {json.dumps(base_itinerary, indent=2)}
                
                User preferences:
                - Budget Level: {preferences.get('budget', 'moderate')}
                - Interests: {', '.join(preferences.get('interests', []))}
                
                Please provide:
                1. A detailed day-by-day itinerary with specific times
                2. Weather-appropriate activity suggestions
                3. Local travel tips
                4. Budget-friendly alternatives where applicable
                5. Relevant cultural insights
                
                Format the response as JSON with these keys:
                {{"itinerary": [list of day objects], "tips": [list of strings]}}
                
                Each day object should have:
                {{"day": number, "activities": [list of activity objects]}}
                
                Each activity object should have:
                {{"time": "HH:MM", "description": "string", "location": "string", "weather_note": "string if relevant"}}"""

                # Get completion from Groq
                completion = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="mixtral-8x7b-32768",
                    temperature=0.7,
                    max_tokens=4000,
                    top_p=1,
                    stream=False
                )

                # Parse the response
                try:
                    enhanced_itinerary = json.loads(completion.choices[0].message.content)
                    return enhanced_itinerary
                except (json.JSONDecodeError, AttributeError, IndexError) as e:
                    print(f"Error parsing Groq response: {str(e)}")
                    if attempt == max_retries - 1:
                        raise

            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    raise

        raise Exception("Failed to enhance itinerary after all retries")

    def generate_itinerary(self, preferences: Dict) -> Dict:
        """Generate a travel itinerary based on user preferences and weather data."""
        try:
            # Get base itinerary from RapidAPI
            rapidapi_key = os.getenv("RAPID_API_KEY")
            if not rapidapi_key:
                raise ValueError("RAPID_API_KEY is missing")

            # Extract preferences
            destination = preferences.get('destination')
            days = preferences.get('days')
            budget = preferences.get('budget', 'moderate')
            interests = preferences.get('interests', [])
            
            if not all([destination, days]):
                raise ValueError("Missing required preferences")

            # Get weather forecast for the travel dates
            weather_data = self.weather_service.get_forecast(destination, days)
            if not weather_data:
                raise ValueError("Could not fetch weather data")

            # Create the prompt for Groq
            prompt = f"""As a luxury travel concierge, create an elegant and detailed itinerary for {days} days in {destination}. 
            
Weather Forecast:
{json.dumps(weather_data, indent=2)}

Traveler Profile:
- Budget Level: {budget}
- Interests: {', '.join(interests)}

Create a sophisticated day-by-day plan that seamlessly integrates weather conditions with carefully curated activities. For each day:
1. Begin with an elegant weather overview
2. Suggest weather-appropriate attire and accessories
3. Plan activities that align with both the weather and traveler interests
4. Include indoor alternatives for weather-sensitive activities
5. Recommend dining experiences that match the ambiance of the day

Please format your response as a JSON object with this structure:
{{
    "itinerary": [
        {{
            "day": {day_num},
            "weather_overview": {{
                "condition": "{weather['condition']}",
                "temperature": "{weather['temp_c']}°C ({weather['temp_f']}°F)",
                "recommendation": "Weather-based recommendation for the day"
            }},
            "activities": [
                {{
                    "time": "HH:MM",
                    "description": "Elegant activity description",
                    "location": "Venue name",
                    "weather_note": "Weather-specific suggestion",
                    "attire": "Recommended attire for this activity"
                }}
            ]
        }} for day_num, weather in enumerate(weather_data, 1)
    ],
    "tips": [
        "Curated travel tips considering weather and preferences"
    ]
}}

Focus on creating a luxurious and memorable experience while ensuring comfort in all weather conditions. Make sure each day's weather_overview accurately reflects the provided weather forecast data."""

            # Get enhanced itinerary from Groq
            completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a sophisticated travel concierge who specializes in creating elegant, weather-aware travel experiences. Always use the exact weather data provided to you."
                    },
                    {"role": "user", "content": prompt}
                ],
                model="mixtral-8x7b-32768",
                temperature=0.7,
                max_tokens=4000
            )

            response = completion.choices[0].message.content
            print("Received enhanced itinerary from Groq")

            try:
                # Parse the response into JSON
                itinerary_data = json.loads(response)
                
                # Ensure weather data is properly integrated
                for day_plan, weather in zip(itinerary_data.get('itinerary', []), weather_data):
                    if 'weather_overview' not in day_plan:
                        day_plan['weather_overview'] = {
                            'condition': weather['condition'],
                            'temperature': f"{weather['temp_c']}°C ({weather['temp_f']}°F)",
                            'recommendation': self._get_weather_recommendation(weather['condition'], weather['temp_c'])
                        }
                
                # Create an elegant weather summary
                weather_summary = "☁️ Weather Forecast Overview ☀️\n\n"
                for day in weather_data:
                    emoji = "🌞" if "sunny" in day['condition'].lower() else "⛅️" if "cloud" in day['condition'].lower() else "🌧️" if "rain" in day['condition'].lower() else "🌤️"
                    weather_summary += f"{emoji} Day {day['day']}: {day['condition']}\n"
                    weather_summary += f"   Temperature: {day['temp_c']}°C ({day['temp_f']}°F)\n"
                    weather_summary += f"   Chance of Rain: {day['chance_of_rain']}%\n\n"

                return {
                    "itinerary": itinerary_data.get('itinerary', []),
                    "tips": itinerary_data.get('tips', []),
                    "weather_summary": weather_summary
                }

            except json.JSONDecodeError as e:
                print(f"Error parsing Groq response: {e}")
                return None

        except Exception as e:
            print(f"Error generating itinerary: {str(e)}")
            return {
                "message": "I apologize, but I encountered an error while generating your itinerary. Please try again.",
                "itinerary": [],
                "tips": [],
                "weather_summary": ""
            }

    def _get_weather_recommendation(self, condition: str, temperature: float) -> str:
        """Generate a weather-based recommendation."""
        condition = condition.lower()
        
        if "rain" in condition:
            return "Pack an umbrella and waterproof clothing. Consider indoor activities during peak rainfall."
        elif "sunny" in condition or "clear" in condition:
            if temperature > 28:
                return "Wear light, breathable clothing. Don't forget sunscreen, sunglasses, and a hat."
            else:
                return "Perfect weather for outdoor activities. Light layers recommended."
        elif "cloud" in condition:
            return "Light layers recommended. Weather is suitable for most outdoor activities."
        else:
            return "Check local weather updates and dress accordingly."
