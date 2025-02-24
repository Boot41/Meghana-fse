import requests
from typing import List, Dict, Set, Tuple, Optional
from math import radians, sin, cos, sqrt, atan2
import itertools
from collections import defaultdict

class ItineraryOptimizer:
    def __init__(self):
        self.visited_places = set()
        self.place_coordinates = {}
        self.place_categories = {}
        self.category_counts = {}
        self.alternative_places = {
            'cultural': [
                {'name': 'ISKCON Temple', 'location': 'Hare Krishna Hill, Rajajinagar', 'category': 'cultural'},
                {'name': 'Bull Temple', 'location': 'Basavanagudi', 'category': 'cultural'},
                {'name': 'Bangalore Palace', 'location': 'Palace Road', 'category': 'cultural'},
                {'name': 'Tipu Sultan Summer Palace', 'location': 'Albert Victor Road', 'category': 'cultural'},
                {'name': 'St. Mary\'s Basilica', 'location': 'Shivajinagar', 'category': 'cultural'}
            ],
            'nature': [
                {'name': 'Lalbagh Botanical Garden', 'location': 'Lalbagh', 'category': 'nature'},
                {'name': 'Cubbon Park', 'location': 'Cubbon Park', 'category': 'nature'},
                {'name': 'Bannerghatta National Park', 'location': 'Bannerghatta Road', 'category': 'nature'},
                {'name': 'Ulsoor Lake', 'location': 'Ulsoor', 'category': 'nature'},
                {'name': 'Hebbal Lake', 'location': 'Hebbal', 'category': 'nature'}
            ],
            'shopping': [
                {'name': 'Commercial Street', 'location': 'Commercial Street', 'category': 'shopping'},
                {'name': 'Brigade Road', 'location': 'Brigade Road', 'category': 'shopping'},
                {'name': 'UB City Mall', 'location': 'Vittal Mallya Road', 'category': 'shopping'},
                {'name': 'Phoenix Marketcity', 'location': 'Whitefield', 'category': 'shopping'},
                {'name': 'Mantri Square Mall', 'location': 'Malleswaram', 'category': 'shopping'}
            ],
            'dining': [
                {'name': 'MTR Restaurant', 'location': 'Lalbagh Road', 'category': 'dining'},
                {'name': 'Vidyarthi Bhavan', 'location': 'Gandhi Bazaar', 'category': 'dining'},
                {'name': 'The Only Place', 'location': 'Museum Road', 'category': 'dining'},
                {'name': 'Mavalli Tiffin Room', 'location': 'Lalbagh Road', 'category': 'dining'},
                {'name': 'Koshy\'s', 'location': 'St. Marks Road', 'category': 'dining'}
            ],
            'entertainment': [
                {'name': 'Innovative Film City', 'location': 'Bidadi', 'category': 'entertainment'},
                {'name': 'Wonderla Amusement Park', 'location': 'Mysore Road', 'category': 'entertainment'},
                {'name': 'HAL Aerospace Museum', 'location': 'Old Airport Road', 'category': 'entertainment'},
                {'name': 'National Gallery of Modern Art', 'location': 'Palace Road', 'category': 'entertainment'},
                {'name': 'Visvesvaraya Industrial Museum', 'location': 'Kasturba Road', 'category': 'entertainment'}
            ]
        }

    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate the distance between two points on Earth using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c
        
    def get_coordinates(self, place: str, city: str) -> Tuple[float, float]:
        """Get latitude and longitude for a place using geocoding"""
        if place in self.place_coordinates:
            return self.place_coordinates[place]
            
        try:
            # Format the search query
            search_query = f"{place}, {city}"
            
            # Use Nominatim API (OpenStreetMap) for geocoding
            url = f"https://nominatim.openstreetmap.org/search"
            params = {
                'q': search_query,
                'format': 'json',
                'limit': 1
            }
            headers = {
                'User-Agent': 'TravelPlanner/1.0'
            }
            
            response = requests.get(url, params=params, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data:
                    lat = float(data[0]['lat'])
                    lon = float(data[0]['lon'])
                    self.place_coordinates[place] = (lat, lon)
                    return (lat, lon)
            
            # Return None if geocoding fails
            return None
            
        except Exception as e:
            print(f"Error getting coordinates for {place}: {str(e)}")
            return None
            
    def get_place_identifier(self, place: Dict) -> str:
        """Generate a unique identifier for a place"""
        return f"{place.get('name', '')}|{place.get('location', '')}".lower()

    def get_place_category(self, place: Dict) -> str:
        """Determine the category of a place based on its name and description"""
        text = f"{place.get('name', '')} {place.get('location', '')} {place.get('description', '')}".lower()
        
        if any(word in text for word in ['temple', 'palace', 'museum', 'art', 'historical']):
            return 'cultural'
        elif any(word in text for word in ['park', 'garden', 'lake', 'hill', 'nature']):
            return 'nature'
        elif any(word in text for word in ['mall', 'shopping', 'market', 'street']):
            return 'shopping'
        elif any(word in text for word in ['restaurant', 'cafe', 'food', 'dining']):
            return 'dining'
        elif any(word in text for word in ['entertainment', 'amusement', 'theatre', 'cinema']):
            return 'entertainment'
        
        return 'other'

    def get_alternative_place(self, category: str, visited_places: Set[str], day_categories: Set[str]) -> Optional[Dict]:
        """Get an alternative place from the same category that hasn't been visited"""
        if category not in self.alternative_places:
            return None
        
        # Try to find a place that hasn't been visited
        for place in self.alternative_places[category]:
            place_id = self.get_place_identifier(place)
            if place_id not in visited_places and category not in day_categories:
                return place
        return None

    def optimize_day_activities(self, activities: List[Dict], visited_places: Set[str]) -> List[Dict]:
        """Optimize a single day's activities for variety and uniqueness"""
        optimized = []
        day_categories = set()
        max_per_category = 2  # Maximum number of places from the same category per day
        
        for activity in activities:
            place_id = self.get_place_identifier(activity)
            category = self.get_place_category(activity)
            
            # Skip if we've already visited this place
            if place_id in visited_places:
                # Try to find an alternative
                alt_place = self.get_alternative_place(category, visited_places, day_categories)
                if alt_place:
                    new_activity = activity.copy()
                    new_activity.update({
                        'name': alt_place['name'],
                        'location': alt_place['location'],
                        'category': alt_place['category'],
                        'note': f"Alternative to {activity['name']} (previously visited)"
                    })
                    optimized.append(new_activity)
                    visited_places.add(self.get_place_identifier(new_activity))
                    day_categories.add(category)
                continue
            
            # Check if we've reached the category limit for this day
            category_count = sum(1 for act in optimized if self.get_place_category(act) == category)
            if category_count >= max_per_category:
                # Try to find an alternative from a different category
                for alt_category in self.alternative_places.keys():
                    if alt_category not in day_categories:
                        alt_place = self.get_alternative_place(alt_category, visited_places, day_categories)
                        if alt_place:
                            new_activity = activity.copy()
                            new_activity.update({
                                'name': alt_place['name'],
                                'location': alt_place['location'],
                                'category': alt_place['category'],
                                'note': f"Alternative activity for better variety"
                            })
                            optimized.append(new_activity)
                            visited_places.add(self.get_place_identifier(new_activity))
                            day_categories.add(alt_category)
                            break
                continue
            
            # Add the original activity
            activity['category'] = category
            optimized.append(activity)
            visited_places.add(place_id)
            day_categories.add(category)
        
        return optimized

    def optimize_day_route(self, places: List[Dict], city: str) -> List[Dict]:
        """Optimize the route for a day's activities using TSP approach"""
        if not places:
            return places
            
        # Get coordinates for all places
        place_coords = []
        for place in places:
            location = place.get('location', '')
            if location:
                coords = self.get_coordinates(location, city)
                if coords:
                    place_coords.append((place, coords))
        
        if len(place_coords) <= 1:
            return places
            
        # Find the optimal route using nearest neighbor algorithm
        current_idx = 0  # Start with the first place
        visited = {0}
        route = [place_coords[0]]
        
        while len(visited) < len(place_coords):
            current_coords = place_coords[current_idx][1]
            min_distance = float('inf')
            next_idx = None
            
            # Find the nearest unvisited place
            for i, (_, coords) in enumerate(place_coords):
                if i not in visited:
                    distance = self.haversine_distance(
                        current_coords[0], current_coords[1],
                        coords[0], coords[1]
                    )
                    if distance < min_distance:
                        min_distance = distance
                        next_idx = i
            
            if next_idx is not None:
                visited.add(next_idx)
                route.append(place_coords[next_idx])
                current_idx = next_idx
        
        # Return places in optimized order
        return [place for place, _ in route]

    def optimize_itinerary(self, itinerary: Dict, city: str) -> Dict:
        """Optimize the full itinerary for better route planning and diversity"""
        optimized_itinerary = {}
        visited_places = set()
        
        # Sort days to ensure we process them in order
        days = sorted([k for k in itinerary.keys() if k.startswith('day_')])
        
        for day_key in days:
            activities = itinerary.get(day_key, [])
            if not isinstance(activities, list):
                continue
            
            # Optimize activities for this day
            optimized_activities = self.optimize_day_activities(activities, visited_places)
            
            # Optimize route if we have coordinates
            optimized_activities = self.optimize_day_route(optimized_activities, city)
            
            # Add travel time estimates
            if len(optimized_activities) > 1:
                for i in range(len(optimized_activities) - 1):
                    current = optimized_activities[i]
                    next_place = optimized_activities[i + 1]
                    current_coords = self.get_coordinates(current['location'], city)
                    next_coords = self.get_coordinates(next_place['location'], city)
                    
                    if current_coords and next_coords:
                        distance = self.haversine_distance(
                            current_coords[0], current_coords[1],
                            next_coords[0], next_coords[1]
                        )
                        # Estimate travel time (assuming average speed of 20 km/h in city)
                        hours = distance / 20
                        minutes = int(hours * 60)
                        current['travel_to_next'] = f"{minutes} minutes"
            
            optimized_itinerary[day_key] = optimized_activities
            
            # Copy over any day-specific metadata
            for key, value in itinerary.items():
                if key.startswith(f"{day_key}_"):
                    optimized_itinerary[key] = value
        
        return optimized_itinerary
