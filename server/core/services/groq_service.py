import os
from typing import List, Dict
import requests
from django.conf import settings

class GroqService:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "mixtral-8x7b-32768"  # Using Mixtral model
        
    def generate_travel_suggestions(self, user_input: str, context: List[Dict] = None) -> Dict:
        """
        Generate travel suggestions using Groq's LLM
        """
        if context is None:
            context = []
            
        messages = [
            {
                "role": "system",
                "content": """You are an expert travel assistant that creates structured travel itineraries. Important rules:
                1. ALWAYS output valid JSON
                2. Use this exact JSON structure:
                   {
                     "days": {
                       "day_1": [{
                         "name": "Activity name",
                         "description": "Detailed description",
                         "location": "Location details",
                         "duration": "Estimated duration",
                         "cost_estimate": "Cost range",
                         "best_time": "Best time to visit",
                         "weather_alternatives": ["Alt 1", "Alt 2"],
                         "local_tips": ["Tip 1", "Tip 2"]
                       }]
                     }
                   }
                3. Every response must be parseable JSON
                4. Do not include any text outside the JSON
                """
            }
        ] + context + [
            {
                "role": "user",
                "content": user_input
            }
        ]
        
        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            )
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Ensure we have valid JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # If not valid JSON, create a basic structure
                return {
                    "error": "Failed to generate valid JSON response",
                    "raw_content": content
                }
            
        except requests.exceptions.RequestException as e:
            return {
                "error": f"Error generating travel suggestions: {str(e)}"
            }
            
    def enhance_itinerary(self, itinerary: Dict) -> Dict:
        """
        Enhance an existing itinerary with additional details and suggestions
        """
        itinerary_str = str(itinerary)
        prompt = f"""Given this travel itinerary:
        {itinerary_str}
        
        Please enhance it by:
        1. Adding local tips and insider recommendations
        2. Suggesting alternative activities for different weather conditions
        3. Including estimated costs and time requirements
        4. Adding cultural context and historical significance
        
        Return the enhanced itinerary in the same JSON structure with added details.
        """
        
        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are a travel expert that enhances itineraries with detailed local knowledge."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            )
            response.raise_for_status()
            
            result = response.json()
            response_text = result["choices"][0]["message"]["content"]
            
            # Extract the JSON part from the response
            import re
            import json
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            
            if json_match:
                try:
                    enhanced_itinerary = json.loads(json_match.group())
                    return enhanced_itinerary
                except json.JSONDecodeError as e:
                    print(f"Error parsing enhanced itinerary: {str(e)}")
                    return itinerary
            else:
                return itinerary
            
        except Exception as e:
            print(f"Error enhancing itinerary: {str(e)}")
            return itinerary  # Return original itinerary if enhancement fails
