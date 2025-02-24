import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import ChatInterface from '../components/Chat/ChatInterface';
import { DayPlan } from '../services/api';

const ChatPage: React.FC = () => {
  const [itinerary, setItinerary] = useState<DayPlan[] | null>(null);
  const location = useLocation();
  const searchQuery = location.state?.searchQuery;

  const handleItineraryGenerated = (newItinerary: DayPlan[]) => {
    console.log('New itinerary received:', newItinerary);
    setItinerary(newItinerary);
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="h-screen flex"
    >
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-4">
        {/* Chat Interface */}
        <div className="lg:col-span-3 h-full border-r border-gray-200">
          <ChatInterface 
            onItineraryGenerated={handleItineraryGenerated}
            initialMessage={searchQuery 
              ? `Hi! I'm your AI travel assistant. I can help you plan your perfect trip to "${searchQuery}".`
              : "Hi! I'm your AI travel assistant. Where would you like to go?"
            }
          />
        </div>

        {/* Itinerary Display */}
        <div className="hidden lg:block p-4 overflow-y-auto h-full bg-gray-50">
          {itinerary ? (
            <div className="space-y-4">
              {itinerary.map((day, index) => (
                <div key={index} className="bg-white rounded-lg p-4 shadow-sm">
                  <h3 className="font-medium text-sm text-gray-500 mb-2">Day {day.day}</h3>
                  {day.weather && (
                    <div className="text-xs text-gray-500 mb-2">
                      {day.weather.condition}, {day.weather.temperature}°C
                    </div>
                  )}
                  <div className="space-y-2">
                    {day.activities.map((activity, actIndex) => (
                      <div key={actIndex} className="border-l-2 border-blue-500 pl-3">
                        <div className="text-xs text-gray-500">{activity.time}</div>
                        <div className="font-medium text-sm">{activity.name}</div>
                        <div className="text-xs text-gray-600">{activity.description}</div>
                        {activity.weather_note && (
                          <div className="text-xs text-blue-600 mt-1">{activity.weather_note}</div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-sm text-gray-500 text-center mt-4">
              Your itinerary will appear here
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default ChatPage;
