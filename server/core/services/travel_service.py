import os
import re
import json
import requests
import logging
import random
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TravelPlannerService:
    """Service for planning travel itineraries using RapidAPI."""
    
    STATES = {
        'INITIAL': 'initial',
        'LOCATION': 'location',
        'TRANSPORT': 'transport',
        'ACTIVITY': 'activity',
        'BUDGET': 'budget',
        'DURATION': 'duration',
        'FOOD_PREFERENCE': 'food_preference',
        'FINAL': 'final'
    }

    def __init__(self, api_key: str):
        """Initialize the service with API key."""
        self.api_key = api_key
        self.base_url = "https://travel-advisor.p.rapidapi.com"
        self.headers = {
            'X-RapidAPI-Key': api_key,
            'X-RapidAPI-Host': 'travel-advisor.p.rapidapi.com'
        }
        logger.info("✅ Initialized TravelPlannerService with RapidAPI")

    def determine_conversation_state(self, user_message: str, current_state: Dict) -> Dict:
        """Determine the next conversation state based on user input."""
        try:
            # Initialize state if empty
            if not current_state:
                current_state = {
                    'state': 'START',
                    'message': "Hi! Where would you like to go?"
                }
            
            current_state_name = current_state.get('state', 'START')
            
            # State machine transitions
            if current_state_name == 'START':
                # Extract location from user message
                location = user_message.strip()
                
                # Validate location
                if len(location) < 3 or any(greeting in location.lower() for greeting in ['hi', 'hello', 'hey']):
                    return {
                        'state': 'START',
                        'message': "Please enter a valid destination city or country. For example: 'Paris' or 'Japan'"
                    }
                
                return {
                    'state': 'DURATION',
                    'location': location,
                    'message': f"Great choice! How many days would you like to spend in {location}?"
                }
                
            elif current_state_name == 'DURATION':
                try:
                    # Extract duration from user message
                    duration = int(''.join(filter(str.isdigit, user_message)))
                    if duration < 1 or duration > 14:
                        return {
                            **current_state,
                            'message': "Please enter a duration between 1 and 14 days."
                        }
                    
                    return {
                        **current_state,
                        'state': 'BUDGET',
                        'duration': duration,
                        'message': "What's your budget level? (low/medium/high)"
                    }
                except ValueError:
                    return {
                        **current_state,
                        'message': "Please enter a number for the duration (e.g., '3 days' or just '3')."
                    }
                
            elif current_state_name == 'BUDGET':
                # Extract budget from user message
                budget = user_message.lower().strip()
                if budget not in ['low', 'medium', 'high']:
                    return {
                        **current_state,
                        'message': "Please specify your budget as 'low', 'medium', or 'high'."
                    }
                
                return {
                    **current_state,
                    'state': 'ACTIVITY',
                    'budget': budget,
                    'message': "What kind of activities interest you? (e.g., culture, food, adventure, shopping, nature)"
                }
                
            elif current_state_name == 'ACTIVITY':
                # Extract activity type from user message
                activity_type = user_message.lower().strip()
                include_food = 'food' in activity_type
                
                return {
                    **current_state,
                    'state': 'FINAL',
                    'activity_type': activity_type,
                    'include_food': include_food
                }
            
            # Default case
            return current_state
            
        except Exception as e:
            logger.error(f"Error in conversation state machine: {str(e)}")
            return {
                'state': 'START',
                'message': "I encountered an error. Let's start over. Where would you like to go?"
            }

    def extract_location(self, message: str) -> Optional[str]:
        """Extract location from message"""
        try:
            logger.info(f"Extracting location from: '{message}'")
            
            # Common Indian cities with variations
            indian_cities = {
                'bangalore': 'Bangalore',
                'bengaluru': 'Bangalore',
                'delhi': 'Delhi',
                'new delhi': 'Delhi',
                'mumbai': 'Mumbai',
                'bombay': 'Mumbai',
                'chennai': 'Chennai',
                'madras': 'Chennai',
                'kolkata': 'Kolkata',
                'calcutta': 'Kolkata',
                'hyderabad': 'Hyderabad',
                'pune': 'Pune',
                'ahmedabad': 'Ahmedabad',
                'jaipur': 'Jaipur',
                'goa': 'Goa'
            }
            
            # First check if any city name is directly mentioned
            message_lower = message.lower().strip()
            logger.info(f"Normalized message: '{message_lower}'")
            
            # Direct city match
            for city_variant, standard_name in indian_cities.items():
                if city_variant in message_lower:
                    logger.info(f"Found direct city match: {standard_name}")
                    return standard_name
            
            # Check for cities with prepositions
            prepositions = ['to', 'in', 'at', 'visit', 'going to', 'traveling to', 'travelling to']
            words = message_lower.split()
            
            for i, word in enumerate(words):
                if word in prepositions and i + 1 < len(words):
                    next_word = words[i + 1]
                    if next_word in indian_cities:
                        logger.info(f"Found city after preposition: {indian_cities[next_word]}")
                        return indian_cities[next_word]
            
            # If it's a single word that's not in our stop words
            if len(words) == 1 and words[0] not in ['hi', 'hello', 'hey']:
                logger.info("Single word input - checking if it's a city")
                if words[0] in indian_cities:
                    logger.info(f"Single word is a city: {indian_cities[words[0]]}")
                    return indian_cities[words[0]]
            
            logger.info("No location found")
            return None
            
        except Exception as e:
            logger.error(f"Error in extract_location: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None

    def extract_transport_preference(self, message: str) -> Optional[str]:
        """Extract transport preference from message"""
        try:
            transport_preferences = ['public', 'private', 'walking', 'mixed']
            message_lower = message.lower()
            for preference in transport_preferences:
                if preference in message_lower:
                    return preference
            return None
        except Exception as e:
            logger.error(f"Error in extract_transport_preference: {str(e)}")
            return None

    def extract_activity_preference(self, message: str) -> Optional[str]:
        """Extract activity preference from message"""
        try:
            activity_preferences = ['adventure', 'relaxing', 'cultural', 'mixed']
            message_lower = message.lower()
            for preference in activity_preferences:
                if preference in message_lower:
                    return preference
            return None
        except Exception as e:
            logger.error(f"Error in extract_activity_preference: {str(e)}")
            return None

    def extract_budget_level(self, message: str) -> Optional[str]:
        """Extract budget level from message"""
        try:
            budget_levels = ['low', 'medium', 'high']
            message_lower = message.lower()
            for level in budget_levels:
                if level in message_lower:
                    return level
            return None
        except Exception as e:
            logger.error(f"Error in extract_budget_level: {str(e)}")
            return None

    def extract_duration(self, message: str) -> Optional[int]:
        """Extract duration from message"""
        try:
            import re
            match = re.search(r'(\d+)(?:\s*days?)?', message)
            if match:
                return int(match.group(1))
            return None
        except Exception as e:
            logger.error(f"Error in extract_duration: {str(e)}")
            return None

    def extract_food_preference(self, message: str) -> Optional[bool]:
        """Extract food preference from message"""
        try:
            message_lower = message.lower()
            if 'yes' in message_lower:
                return True
            elif 'no' in message_lower:
                return False
            return None
        except Exception as e:
            logger.error(f"Error in extract_food_preference: {str(e)}")
            return None

    def get_travel_plan(
        self,
        destination: str,
        duration: int,
        budget: str,
        activity_type: str,
        include_food: bool = False,
        weather_data: Dict = None
    ) -> Dict:
        """Get a travel plan for the specified destination."""
        try:
            logger.info(f"🌍 Getting travel plan for {destination} for {duration} days")
            
            # Validate inputs
            if not destination:
                raise ValueError("Destination is required")
            if not duration or duration < 1:
                raise ValueError("Duration must be at least 1 day")
            if not budget in ['low', 'medium', 'high']:
                budget = 'medium'  # Default to medium budget
            
            # Clean destination name
            destination = destination.strip().lower()
            
            # Build the request URL
            url = f"{self.base_url}/v1/places"
            
            # Prepare query parameters
            querystring = {
                "location": destination,
                "limit": "30",
                "offset": "0",
                "radius": "5",
                "language": "en",
                "currency": "USD"
            }
            
            logger.info(f"🔍 Searching for places in {destination}...")
            
            # Make the API request
            response = requests.get(
                url,
                headers=self.headers,
                params=querystring,
                timeout=10  # Add timeout
            )
            
            # Check if request was successful
            if response.status_code != 200:
                logger.error(f"❌ API request failed with status {response.status_code}: {response.text}")
                raise Exception(f"Failed to get places data: {response.text}")
            
            # Parse response
            data = response.json()
            logger.info(f"✅ Found {len(data.get('data', []))} places")
            
            if not data.get('data'):
                logger.warning(f"⚠️ No places found for {destination}")
                return None
            
            # Process places data
            places = data['data']
            
            # Group places by category
            categorized_places = self._categorize_places(places)
            
            # Create daily itinerary
            itinerary = []
            
            # Get weather data for each day if available
            daily_weather = weather_data.get('daily', []) if weather_data else []
            
            for day in range(1, duration + 1):
                # Get weather for this day
                day_weather = daily_weather[day - 1] if day <= len(daily_weather) else None
                
                # Create activities for the day based on weather
                activities = self._create_day_activities(
                    categorized_places,
                    activity_type,
                    include_food,
                    day_weather
                )
                
                # Add day plan
                day_plan = {
                    'day': day,
                    'activities': activities,
                    'weather': day_weather
                }
                
                itinerary.append(day_plan)
            
            logger.info(f"✅ Successfully created {duration}-day itinerary for {destination}")
            
            return {
                'destination': destination,
                'duration': duration,
                'itinerary': itinerary,
                'budget': budget
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error while getting travel plan: {str(e)}")
            raise Exception(f"Network error while getting travel data: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Error getting travel plan: {str(e)}")
            raise

    def get_places(self, destination: str, activity_type: str) -> List[Dict]:
        """Get places from RapidAPI."""
        try:
            logger.info(f"🌍 Getting places for {destination} with activity type: {activity_type}")
            
            # Create headers for RapidAPI
            headers = {
                'X-RapidAPI-Key': self.api_key,
                'X-RapidAPI-Host': 'travel-advisor.p.rapidapi.com'
            }
            
            # Map activity types to interests
            activity_to_interests = {
                'adventure': ['adventure sports', 'hiking', 'outdoor activities'],
                'culture': ['history', 'art', 'museums', 'temples'],
                'food': ['restaurants', 'food tours', 'cafes'],
                'shopping': ['shopping', 'markets', 'malls'],
                'nature': ['parks', 'gardens', 'wildlife'],
                'relaxing': ['spa', 'beaches', 'leisure'],
                'mixed': ['sightseeing', 'popular attractions']
            }
            
            # Get interests based on activity type
            interests = activity_to_interests.get(activity_type.lower(), ['sightseeing'])
            
            # Make API request for travel plan
            payload = {
                'days': 4,  # Default to 4 days
                'destination': destination,
                'interests': interests,
                'budget': 'medium',  # Default to medium budget
                'travelMode': 'public transport'  # Default to public transport
            }
            
            logger.info(f"Sending request to RapidAPI with payload: {payload}")
            
            response = requests.post(
                f"{self.base_url}/plan",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                places = []
                
                # Extract places from the itinerary
                if 'plan' in data:
                    for day in data['plan']:
                        for activity in day.get('activities', []):
                            place = {
                                'name': activity.get('name', ''),
                                'description': activity.get('description', ''),
                                'type': activity.get('type', 'tourist_attraction'),
                                'rating': activity.get('rating', 4.0)
                            }
                            if place['name'] and place not in places:
                                places.append(place)
                
                logger.info(f"📍 Found {len(places)} places in {destination}")
                return places
            else:
                logger.warning(f"⚠️ Failed to get places: {response.text}")
                # Fall back to default places for Bangalore
                if destination.lower() in ['bangalore', 'bengaluru']:
                    return [
                        {
                            "name": "Lalbagh Botanical Garden",
                            "description": "Historic garden with diverse plant species and a glass house",
                            "rating": 4.5,
                            "type": "park"
                        },
                        {
                            "name": "Cubbon Park",
                            "description": "Large urban park with walking trails and monuments",
                            "rating": 4.4,
                            "type": "park"
                        },
                        {
                            "name": "Bangalore Palace",
                            "description": "Tudor-style palace with beautiful architecture",
                            "rating": 4.3,
                            "type": "tourist_attraction"
                        },
                        {
                            "name": "ISKCON Temple Bangalore",
                            "description": "Modern Hindu temple complex with cultural center",
                            "rating": 4.6,
                            "type": "place_of_worship"
                        },
                        {
                            "name": "UB City",
                            "description": "Luxury shopping mall and dining destination",
                            "rating": 4.5,
                            "type": "shopping_mall"
                        }
                    ]
                return []
            
        except Exception as e:
            logger.error(f"❌ Error getting places: {str(e)}")
            return []

    def _categorize_places(self, places: List[Dict]) -> Dict[str, List[Dict]]:
        """Group places by category."""
        categories = {
            'attractions': [],
            'restaurants': [],
            'shopping': [],
            'entertainment': [],
            'nature': [],
            'cultural': []
        }
        
        for place in places:
            category = place.get('category', '').lower()
            
            if any(word in category for word in ['restaurant', 'cafe', 'food']):
                categories['restaurants'].append(place)
            elif any(word in category for word in ['shop', 'mall', 'market']):
                categories['shopping'].append(place)
            elif any(word in category for word in ['park', 'garden', 'beach', 'mountain']):
                categories['nature'].append(place)
            elif any(word in category for word in ['museum', 'temple', 'church', 'historic']):
                categories['cultural'].append(place)
            elif any(word in category for word in ['cinema', 'theater', 'club', 'entertainment']):
                categories['entertainment'].append(place)
            else:
                categories['attractions'].append(place)
        
        return categories

    def _create_day_activities(self, categorized_places: Dict[str, List[Dict]], activity_type: str, include_food: bool, weather: Dict = None) -> List[Dict]:
        """Create a list of activities for a day based on preferences and weather."""
        activities = []
        
        # Define time slots
        time_slots = [
            ('09:00', 'Morning'),
            ('12:00', 'Lunch'),
            ('14:00', 'Afternoon'),
            ('17:00', 'Evening'),
            ('19:00', 'Dinner')
        ]
        
        # Weather-based activity selection
        is_good_weather = True
        weather_note = ""
        if weather:
            condition = weather.get('condition', '').lower()
            is_good_weather = not any(bad_weather in condition for bad_weather in ['rain', 'storm', 'snow'])
            if not is_good_weather:
                weather_note = f"Note: {condition} forecast. Consider indoor activities."
        
        # Select places based on activity type and weather
        for time, period in time_slots:
            activity = None
            
            if period in ['Lunch', 'Dinner'] and include_food:
                if categorized_places['restaurants']:
                    restaurant = random.choice(categorized_places['restaurants'])
                    activity = {
                        'time': time,
                        'name': restaurant.get('name', ''),
                        'description': restaurant.get('description', 'Enjoy local cuisine'),
                        'type': 'food',
                        'weather_note': ''
                    }
            else:
                # Select category based on activity type and weather
                if activity_type == 'culture':
                    preferred_categories = ['cultural', 'attractions']
                elif activity_type == 'nature':
                    preferred_categories = ['nature', 'attractions'] if is_good_weather else ['cultural', 'entertainment']
                elif activity_type == 'shopping':
                    preferred_categories = ['shopping', 'entertainment']
                else:  # mixed
                    preferred_categories = list(categorized_places.keys())
                
                # Try to get a place from preferred categories
                for category in preferred_categories:
                    if categorized_places[category]:
                        place = random.choice(categorized_places[category])
                        activity = {
                            'time': time,
                            'name': place.get('name', ''),
                            'description': place.get('description', ''),
                            'type': category,
                            'weather_note': weather_note if not is_good_weather and category == 'nature' else ''
                        }
                        break
            
            if activity:
                activities.append(activity)
        
        return activities
