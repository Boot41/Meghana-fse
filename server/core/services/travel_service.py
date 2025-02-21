import json
from datetime import datetime
from typing import Dict, List, Optional
import requests
from django.conf import settings

class TravelPlannerService:
    def __init__(self):
        self.api_base_url = settings.OPENTRIP_API_URL
        self.api_key = settings.OPENTRIP_API_KEY

    def extract_travel_params(self, user_message: str) -> Dict:
        """
        Extract travel parameters from user's natural language input
        Returns a dictionary with extracted parameters
        """
        # In a real implementation, this would use NLP to extract parameters
        # For now, we'll use basic string matching
        params = {
            'duration': None,
            'location': None,
            'preferences': [],
            'budget_level': None
        }
        
        message = user_message.lower()
        
        # Extract duration (assuming format: "X-day" or "X day")
        import re
        duration_match = re.search(r'(\d+)[ -]day', message)
        if duration_match:
            params['duration'] = int(duration_match.group(1))
            
        # Extract location (assuming it's a capitalized word not at the start)
        words = user_message.split()
        for word in words:
            if word[0].isupper() and words.index(word) != 0:
                params['location'] = word
                break
                
        # Extract preferences
        preference_keywords = {
            'budget': 'budget_friendly',
            'luxury': 'luxury',
            'sightseeing': 'sightseeing',
            'culture': 'cultural',
            'food': 'culinary',
            'adventure': 'adventure',
            'outdoor': 'outdoor'
        }
        
        for keyword, pref in preference_keywords.items():
            if keyword in message:
                params['preferences'].append(pref)
                
        # Determine budget level
        budget_keywords = {
            'budget': 'low',
            'cheap': 'low',
            'luxury': 'high',
            'expensive': 'high',
            'moderate': 'medium',
            'mid': 'medium'
        }
        
        for keyword, level in budget_keywords.items():
            if keyword in message:
                params['budget_level'] = level
                break
                
        return params

    def generate_itinerary(self, params: Dict) -> Dict:
        """
        Generate a travel itinerary using OpenTripPlanner API and enhance with Groq
        """
        try:
            print(f"Received params: {params}")
            
            # Validate required parameters
            if not params.get('destination'):
                return {"error": "Destination is required"}
            if not params.get('duration'):
                return {"error": "Duration is required"}
            
            # Convert form data to internal format
            internal_params = {
                'destination': params.get('destination', ''),
                'duration': int(params.get('duration', 0)),
                'interests': params.get('interests', []),
                'budget': params.get('budget', 'medium'),
                'dates': params.get('travelDates', ''),
                'style': params.get('travelStyle', 'balanced')
            }
            
            print(f"Internal params: {internal_params}")
            
            # Generate basic itinerary with Groq
            from .groq_service import GroqService
            groq = GroqService()
            
            # Create the basic prompt
            prompt = f"Create a {internal_params['duration']}-day travel itinerary for {internal_params['destination']}. "
            if internal_params['interests']:
                prompt += f"Include activities related to: {', '.join(internal_params['interests'])}. "
            prompt += f"Budget level: {internal_params['budget']}. Travel style: {internal_params['style']}. "
            
            # Add structure requirements
            prompt += "\nFormat the response as a JSON object with this exact structure:"
            prompt += "\n{"
            prompt += "\n  \"days\": {"
            prompt += "\n    \"day_1\": [{"
            prompt += "\n      \"name\": \"Activity name\","
            prompt += "\n      \"description\": \"Detailed description\","
            prompt += "\n      \"location\": \"Location details\","
            prompt += "\n      \"duration\": \"Estimated duration\","
            prompt += "\n      \"cost_estimate\": \"Cost range\","
            prompt += "\n      \"best_time\": \"Best time to visit\","
            prompt += "\n      \"weather_alternatives\": [\"Alt 1\", \"Alt 2\"],"
            prompt += "\n      \"local_tips\": [\"Tip 1\", \"Tip 2\"]"
            prompt += "\n    }]"
            prompt += "\n  }"
            prompt += "\n}"
            
            # Try to get itinerary from OpenTripPlanner first
            try:
                planner_data = self._get_opentrip_itinerary(internal_params)
                print(f"OpenTripPlanner data: {planner_data}")
            except Exception as e:
                print(f"OpenTripPlanner error: {str(e)}")
                planner_data = None
                
            # Now use Groq to enhance or create the itinerary
            from .groq_service import GroqService
            groq = GroqService()
            
            if planner_data:
                # Create prompt to enhance OpenTripPlanner data
                prompt = self._create_enhancement_prompt(planner_data, internal_params)
            else:
                # Create prompt for basic itinerary
                prompt = self._create_basic_prompt(internal_params)
                
            # Get enhanced/generated itinerary from Groq
            result = groq.generate_travel_suggestions(prompt)
            
            # Check for errors
            if "error" in result:
                return result
                
            # Format the response
            return {
                "summary": f"{internal_params['duration']}-day itinerary for {internal_params['destination']}",
                "overview": {
                    "destination": internal_params['destination'],
                    "duration": internal_params['duration'],
                    "interests": internal_params['interests'],
                    "budget": internal_params['budget'],
                    "style": internal_params['style']
                },
                "days": result.get("days", {})
            }
            try:
                from .groq_service import GroqService
                groq = GroqService()
                prompt = self._create_enhancement_prompt(planner_data, internal_params)
                enhanced_data = groq.generate_travel_suggestions(prompt)
                print(f"Groq enhancement: {enhanced_data}")
            except Exception as e:
                print(f"Groq enhancement error: {str(e)}")
                enhanced_data = planner_data.get('basic_plan', '')
            
            # Structure the final itinerary
            return self._structure_enhanced_itinerary(planner_data, enhanced_data, internal_params)
            
        except ValueError as e:
            error_msg = str(e)
            print(f"Validation error: {error_msg}")
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Failed to generate itinerary: {str(e)}"
            print(f"Unexpected error: {error_msg}")
            return {"error": error_msg}
                
        except Exception as e:
            # Handle all errors gracefully
            return self._generate_fallback_response(params, str(e))

    def _structure_itinerary(self, raw_itinerary: Dict, duration: int) -> Dict:
        """
        Structure the raw API response into a user-friendly format
        """
        structured_itinerary = {
            "summary": f"{duration}-day personalized itinerary",
            "days": []
        }

        # Process each day's activities
        for day in range(duration):
            day_activities = raw_itinerary.get(f'day_{day+1}', [])
            
            structured_day = {
                "day_number": day + 1,
                "theme": self._get_day_theme(day_activities),
                "activities": self._format_activities(day_activities)
            }
            
            structured_itinerary["days"].append(structured_day)

        return structured_itinerary

    def _get_day_theme(self, activities: List) -> str:
        """
        Generate a theme for the day based on activities
        """
        # This would be more sophisticated in production
        themes = {
            "sightseeing": "🏛️ Cultural Exploration",
            "outdoor": "🌲 Outdoor Adventure",
            "food": "🍜 Culinary Journey",
            "shopping": "🛍️ Shopping & Local Markets",
            "relaxation": "🌅 Relaxation & Wellness"
        }
        
        # Default theme if we can't determine one
        return themes.get("sightseeing")

    def _format_activities(self, activities: List) -> List[Dict]:
        """
        Format raw activities into structured format
        """
        formatted = []
        for activity in activities:
            formatted.append({
                "name": activity.get("name", ""),
                "description": activity.get("description", ""),
                "duration": activity.get("duration", ""),
                "cost_estimate": activity.get("cost", ""),
                "location": activity.get("location", ""),
                "tips": activity.get("tips", [])
            })
        return formatted

    def _generate_fallback_response(self, params: Dict, error: str) -> Dict:
        """
        Generate a fallback response when API fails
        """
        return {
            "error": "Unable to fetch real-time itinerary",
            "fallback": {
                "message": "Here's a general suggestion based on your preferences",
                "suggestion": self._generate_generic_suggestion(params)
            }
        }

    def _generate_generic_suggestion(self, params: Dict) -> str:
        """
        Generate a generic suggestion when API is unavailable
        """
        location = params.get('location', 'your destination')
        duration = params.get('duration', 'your trip')
        preferences = params.get('preferences', [])
        
        suggestion = f"For your {duration}-day trip to {location}, I recommend:\n"
        
        if 'sightseeing' in preferences:
            suggestion += "- Visit main tourist attractions in the morning\n"
        if 'food' in preferences:
            suggestion += "- Explore local restaurants and food markets\n"
        if 'culture' in preferences:
            suggestion += "- Experience local cultural activities\n"
        
        return suggestion
        
    def _get_opentrip_itinerary(self, params: Dict) -> Dict:
        """Get initial itinerary from OpenTripPlanner API via RapidAPI"""
        try:
            endpoint = f"{self.api_base_url}/plan"
            headers = {
                "X-RapidAPI-Key": self.api_key,
                "X-RapidAPI-Host": "opentripplanner1.p.rapidapi.com",
                "Content-Type": "application/json"
            }
            
            # Format parameters for OpenTripPlanner API
            api_params = {
                "destination": params['destination'],
                "duration": params['duration'],
                "preferences": params['interests'],
                "budget": params['budget'],
                "dates": params['dates'],
                "style": params['style']
            }
            
            print(f"Calling OpenTripPlanner API with params: {api_params}")
            response = requests.post(endpoint, json=api_params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            print(f"OpenTripPlanner API response: {data}")
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"OpenTripPlanner API error: {str(e)}")
            if hasattr(e.response, 'text'):
                print(f"Error response: {e.response.text}")
            raise
            
    def _create_basic_prompt(self, params: Dict) -> str:
        """Create a prompt for generating a basic itinerary"""
        prompt = f"Create a detailed {params['duration']}-day travel itinerary for {params['destination']}. "
        
        if params['interests']:
            prompt += f"Include activities related to: {', '.join(params['interests'])}. "
        
        prompt += f"Budget level: {params['budget']}. Travel style: {params['style']}. "
        
        if params['dates']:
            prompt += f"Travel dates: {params['dates']}. "
        
        prompt += "\nFor each day, provide:\n"
        prompt += "1. A theme for the day\n"
        prompt += "2. 3-4 main activities with descriptions\n"
        prompt += "3. Suggested timing for each activity\n"
        prompt += "4. Location details\n"
        prompt += "5. Cost estimates\n"
        prompt += "\nFormat the response as a JSON object with days as keys."
        
        return prompt
        
    def _create_enhancement_prompt(self, planner_data: Dict, params: Dict) -> str:
        """Create a prompt for Groq to enhance the itinerary"""
        prompt = f"Enhance this {params['duration']}-day travel itinerary for {params['destination']}:\n\n"
        
        # Add the base itinerary to the prompt
        prompt += json.dumps(planner_data, indent=2) + "\n\n"
        
        prompt += "Please enhance this itinerary by:\n"
        prompt += "1. Adding local insights and cultural context\n"
        prompt += "2. Suggesting alternative activities for different weather conditions\n"
        prompt += "3. Adding specific tips for each activity\n"
        prompt += "4. Estimating costs and suggesting budget-friendly alternatives\n"
        prompt += "5. Adding recommended times for each activity\n"
        
        if params['interests']:
            prompt += f"\nFocus on these interests: {', '.join(params['interests'])}\n"
        
        prompt += "\nKeep the same basic structure but add your enhancements to each day and activity."
            
        if params.get('interests'):
            interests = ', '.join(params['interests'])
            prompt += f"The traveler is interested in: {interests}. "
            
        if params.get('travelDates'):
            prompt += f"The trip is planned for {params['travelDates']}. "
            
        if params.get('travelStyle'):
            prompt += f"The preferred travel style is {params['travelStyle']}. "
            
        prompt += """Please provide:
        1. A day-by-day itinerary
        2. Estimated timings for each activity
        3. Budget considerations
        4. Local tips and cultural insights
        5. Alternative options for bad weather
        6. Transportation suggestions between locations"""
            
        return prompt
        
    def _merge_itineraries(self, groq_itinerary: str, planner_data: Dict) -> Dict:
        """Merge Groq suggestions with OpenTripPlanner data"""
        try:
            # Convert Groq's text response to structured data
            structured_groq = self._parse_groq_response(groq_itinerary)
            
            # Start with the OpenTripPlanner data as base
            merged = planner_data.copy()
            
            # Enhance each day with Groq's suggestions
            for day_num in range(len(merged.get('days', []))):
                planner_day = merged['days'][day_num]
                groq_day = structured_groq.get('days', [])[day_num] if day_num < len(structured_groq.get('days', [])) else None
                
                if groq_day:
                    # Add Groq's suggestions to each activity
                    for activity in planner_day.get('activities', []):
                        matching_groq_activity = self._find_matching_activity(activity, groq_day.get('activities', []))
                        if matching_groq_activity:
                            activity.update({
                                'local_tips': matching_groq_activity.get('tips', []),
                                'cultural_context': matching_groq_activity.get('cultural_context', ''),
                                'weather_alternatives': matching_groq_activity.get('weather_alternatives', []),
                                'best_time': matching_groq_activity.get('best_time', '')
                            })
            
            # Add overall trip insights from Groq
            merged.update({
                'trip_overview': structured_groq.get('overview', ''),
                'cultural_notes': structured_groq.get('cultural_notes', []),
                'packing_suggestions': structured_groq.get('packing_suggestions', []),
                'local_customs': structured_groq.get('local_customs', [])
            })
            
            return merged
            
        except Exception as e:
            print(f"Error merging itineraries: {str(e)}")
            return planner_data
            
    def _parse_groq_response(self, response: str) -> Dict:
        """Parse Groq's text response into structured data"""
        try:
            # Use Groq to structure its own response
            from .groq_service import GroqService
            groq = GroqService()
            
            prompt = f"""Convert this travel itinerary into a structured JSON format:
            {response}
            
            The JSON should have this structure:
            {{
                "overview": "General trip overview",
                "days": [
                    {{
                        "day_number": 1,
                        "theme": "Day theme",
                        "activities": [
                            {{
                                "name": "Activity name",
                                "description": "Activity description",
                                "duration": "Estimated duration",
                                "cost_estimate": "Cost range",
                                "tips": ["Local tip 1", "Local tip 2"],
                                "cultural_context": "Cultural significance",
                                "weather_alternatives": ["Alternative 1", "Alternative 2"],
                                "best_time": "Best time to visit"
                            }}
                        ]
                    }}
                ],
                "cultural_notes": ["Cultural note 1", "Cultural note 2"],
                "packing_suggestions": ["Packing item 1", "Packing item 2"],
                "local_customs": ["Custom 1", "Custom 2"]
            }}"""
            
            structured_response = groq.generate_travel_suggestions(prompt)
            
            # Extract the JSON part from the response
            import re
            json_match = re.search(r'\{[\s\S]*\}', structured_response)
            if json_match:
                import json
                return json.loads(json_match.group())
            else:
                return {}
                
        except Exception as e:
            print(f"Error parsing Groq response: {str(e)}")
            return {}
            
    def _find_matching_activity(self, planner_activity: Dict, groq_activities: List[Dict]) -> Optional[Dict]:
        """Find matching activity from Groq's suggestions"""
        from difflib import SequenceMatcher
        
        def similarity(a: str, b: str) -> float:
            return SequenceMatcher(None, a.lower(), b.lower()).ratio()
        
        planner_name = planner_activity.get('name', '')
        best_match = None
        best_score = 0
        
        for groq_activity in groq_activities:
            groq_name = groq_activity.get('name', '')
            score = similarity(planner_name, groq_name)
            
            if score > best_score and score > 0.6:  # 60% similarity threshold
                best_score = score
                best_match = groq_activity
                
        return best_match
        
    def _structure_groq_response(self, response: str, duration: int) -> Dict:
        """Structure Groq's response into itinerary format"""
        structured_data = self._parse_groq_response(response)
        
        # Ensure we have the correct number of days
        while len(structured_data.get('days', [])) < duration:
            day_number = len(structured_data['days']) + 1
            structured_data['days'].append({
                'day_number': day_number,
                'theme': f'Day {day_number}',
                'activities': []
            })
            
        # Truncate if we have too many days
        structured_data['days'] = structured_data['days'][:duration]
        
        return structured_data
