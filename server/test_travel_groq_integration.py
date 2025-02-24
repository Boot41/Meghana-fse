import os
import requests
import logging
from dotenv import load_dotenv
from colorama import Fore, Style

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def fetch_weather(location):
    """Fetches weather details for a given location."""
    try:
        weather_api_key = os.getenv("WEATHER_API_KEY")
        if not weather_api_key:
            logging.error("WEATHER_API_KEY is missing from environment variables.")
            return None
        
        url = f"https://api.weatherapi.com/v1/forecast.json?key={weather_api_key}&q={location}&days=3"
        logging.info(f"🌤️ Fetching weather data for {location}...")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        weather_data = data.get("forecast", {}).get("forecastday", [])
        if weather_data:
            logging.info(f"✅ Successfully got weather data for {location}")
            for day in weather_data:
                logging.info(f"📅 {day['date']}: {day['day']['condition']['text']}, Max: {day['day']['maxtemp_c']}°C")
        return weather_data
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching weather data: {e}")
        return None

def fetch_itinerary(destination, days, budget, interests):
    """Fetches AI-generated itinerary from RapidAPI."""
    try:
        rapidapi_key = os.getenv("RAPID_API_KEY")
        if not rapidapi_key:
            logging.error("RAPID_API_KEY is missing from environment variables.")
            return None

        url = "https://ai-trip-planner.p.rapidapi.com/detailed-plan"
        headers = {
            "X-RapidAPI-Key": rapidapi_key,
            "X-RapidAPI-Host": "ai-trip-planner.p.rapidapi.com",
            "Content-Type": "application/json"
        }
        
        logging.info(f"🌍 Fetching travel data for {destination} from RapidAPI...")
        
        # Clean and normalize inputs
        destination = destination.strip().title()
        days = int(days)
        budget = budget.strip().lower()
        
        # Validate budget
        valid_budgets = {"low", "medium", "high"}
        if budget not in valid_budgets:
            budget = "medium"  # Default to medium if invalid
        
        # Convert interests string to list and clean it
        if isinstance(interests, str):
            interests = [interest.strip().lower() for interest in interests.split(',')]
        
        # Define valid API interests
        valid_api_interests = {
            "art", "theater", "museums", "history", "architecture", "cultural events",
            "hiking", "wildlife", "beaches", "national parks", "adventure sports",
            "cuisine", "street food", "wine tasting", "breweries", "fine dining",
            "spa", "yoga retreats", "relaxation", "resorts",
            "shopping", "luxury brands", "local markets",
            "theme parks", "zoos", "kid-friendly activities",
            "bars", "clubs", "live music", "theater shows",
            "sports events", "fitness", "cycling",
            "tech", "innovation", "conventions",
            "photography", "scenic views"
        }
        
        # Map common terms to valid API interests
        interest_mapping = {
            'food': ['cuisine', 'street food', 'fine dining'],
            'culture': ['cultural events', 'art', 'museums'],
            'nature': ['hiking', 'wildlife', 'scenic views'],
            'adventure': ['adventure sports', 'hiking', 'cycling'],
            'shopping': ['shopping', 'local markets', 'luxury brands'],
            'entertainment': ['theater shows', 'live music', 'bars'],
            'relaxation': ['spa', 'yoga retreats', 'relaxation'],
            'history': ['history', 'museums', 'architecture'],
            'sports': ['sports events', 'fitness', 'cycling'],
            'technology': ['tech', 'innovation', 'conventions']
        }
        
        # Process interests
        valid_interests = []
        for interest in interests:
            interest = interest.strip().lower()
            # Check if it's a mapped interest
            if interest in interest_mapping:
                valid_interests.extend(interest_mapping[interest])
            # Check if it's a valid API interest
            elif interest in valid_api_interests:
                valid_interests.append(interest)
        
        # Remove duplicates and ensure we have valid interests
        valid_interests = list(set(valid_interests))
        if not valid_interests:
            valid_interests = ["history", "cuisine", "local markets"]
        
        # Construct payload
        payload = {
            "days": days,
            "destination": destination,
            "interests": valid_interests[:2],  # API accepts max 2 interests
            "budget": budget,
            "travelMode": "public transport"  # Default travel mode
        }
        
        logging.info(f"Sending request to RapidAPI with payload: {payload}")
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            logging.error(f"API Error: Status {response.status_code}, Response: {response.text}")
            return None
            
        data = response.json()
        if data:
            logging.info(f"✅ Successfully got travel data from RapidAPI")
            logging.info(f"📍 Number of places fetched: {len(data.get('places', []))}")
            for place in data.get('places', [])[:3]:  # Show first 3 places
                logging.info(f"🏛️ {place.get('name')}: {place.get('category')}")
        
        return data.get("plan", {}).get("itinerary", [])
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching itinerary: {e}")
        return None

def enhance_itinerary_with_groq(itinerary, weather, preferences):
    """Enhances the itinerary with AI-powered recommendations using Groq."""
    try:
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            logging.error("GROQ_API_KEY is missing from environment variables.")
            return "Could not enhance itinerary: Missing API key."

        # Format the itinerary and weather data for the prompt
        itinerary_text = ""
        for day_num, (day_plan, day_weather) in enumerate(zip(itinerary, weather or []), 1):
            itinerary_text += f"\nDay {day_num}:\n"
            for activity in day_plan.get('activities', []):
                itinerary_text += f"- {activity.get('time')}: {activity.get('activity')} at {activity.get('location')}\n"
            if day_weather:
                weather_condition = day_weather.get('day', {}).get('condition', {}).get('text', 'N/A')
                max_temp = day_weather.get('day', {}).get('maxtemp_c', 'N/A')
                min_temp = day_weather.get('day', {}).get('mintemp_c', 'N/A')
                itinerary_text += f"Weather: {weather_condition}, Max: {max_temp}°C, Min: {min_temp}°C\n"

        # Create the prompt for Groq
        prompt = f"""As a travel expert, please analyze this itinerary and provide 3 specific recommendations to enhance the trip, considering the weather conditions and the traveler's interests in {', '.join(preferences)}:

Itinerary:
{itinerary_text}

Please provide:
1. A specific dining recommendation based on the weather and local specialties
2. A suggestion for the best time to visit certain attractions based on weather
3. An alternative indoor activity suggestion for bad weather days

Format your response in clear bullet points."""

        # Make request to Groq API
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {groq_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "mixtral-8x7b-32768",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 500
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        if "choices" in result and result["choices"]:
            return result["choices"][0]["message"]["content"]
        else:
            return "Could not generate recommendations."

    except requests.exceptions.RequestException as e:
        logging.error(f"Error enhancing itinerary with Groq: {e}")
        return "Could not enhance itinerary due to API error."
    except Exception as e:
        logging.error(f"Unexpected error in Groq enhancement: {e}")
        return "Could not process itinerary enhancement."

def main():
    """Main function to run the travel planner."""
    print(f"{Fore.GREEN}Welcome to the AI Travel Itinerary Planner!{Style.RESET_ALL}")
    
    # Get user input
    destination = input("Enter your destination: ")
    days = input("How many days will you be traveling? ")
    budget = input("Enter your budget (low, medium, high): ")
    interests = input("What are your interests (e.g., adventure, history, food)? ")
    
    print("\nFetching itinerary and weather data...")
    
    # Fetch weather data
    weather = fetch_weather(destination)
    if not weather:
        print("Could not fetch weather data. Proceeding with itinerary only.")
    
    # Fetch and enhance itinerary
    itinerary = fetch_itinerary(destination, days, budget, interests)
    if not itinerary:
        print("Could not generate itinerary. Please check API responses.")
        return
    
    # Display the enhanced itinerary
    print(f"\n{Fore.BLUE}Here's your personalized travel itinerary for {destination}:{Style.RESET_ALL}\n")
    
    for day_num, day_plan in enumerate(itinerary, 1):
        print(f"{Fore.YELLOW}Day {day_num}:{Style.RESET_ALL}")
        activities = day_plan.get("activities", [])
        for activity in activities:
            print(f"- {activity.get('time', 'Flexible')}: {activity.get('activity', '')}")
            if activity.get('location'):
                print(f"  Location: {activity.get('location')}")
            if activity.get('note'):
                print(f"  Note: {activity.get('note')}")
        print()
        
        # Display weather if available
        if weather and len(weather) >= day_num:
            day_weather = weather[day_num - 1]
            print(f"{Fore.CYAN}Weather: {day_weather.get('day', {}).get('condition', {}).get('text', 'N/A')}")
            print(f"Max: {day_weather.get('day', {}).get('maxtemp_c', 'N/A')}°C")
            print(f"Min: {day_weather.get('day', {}).get('mintemp_c', 'N/A')}°C{Style.RESET_ALL}\n")
    
    print(f"\n{Fore.YELLOW}Enhancing itinerary with AI recommendations...{Style.RESET_ALL}")
    ai_enhancements = enhance_itinerary_with_groq(itinerary, weather, interests)
    print(f"{Fore.CYAN}AI-Powered Recommendations:\n{ai_enhancements}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}Safe travels!{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
