import React from 'react';
import { motion } from 'framer-motion';

interface ItineraryDisplayProps {
  itinerary: {
    destination: string;
    duration: number;
    budget: string;
    activity_type: string;
    itinerary: string;
  };
}

const ItineraryDisplay: React.FC<ItineraryDisplayProps> = ({ itinerary }) => {
  // Parse the itinerary text into days
  const days = itinerary.itinerary
    .split('\n\nDay')
    .filter(Boolean)
    .map(day => {
      const [dayHeader, ...activities] = day.split('\n');
      return {
        dayNumber: dayHeader.includes('Day') ? parseInt(dayHeader) : 1,
        activities: activities
          .filter(activity => activity.trim().startsWith('-'))
          .map(activity => {
            const [time, ...rest] = activity.replace('-', '').trim().split(':');
            const [description, location] = rest.join(':').split(' at ');
            return {
              time: time.trim(),
              description: description.trim(),
              location: location?.trim() || ''
            };
          })
      };
    });

  return (
    <div className="space-y-6 p-6">
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg p-6 text-white">
        <h2 className="text-2xl font-bold mb-2">
          {itinerary.destination.charAt(0).toUpperCase() + itinerary.destination.slice(1)}
        </h2>
        <p className="text-blue-100">
          {itinerary.duration} Day Trip • {itinerary.budget.charAt(0).toUpperCase() + itinerary.budget.slice(1)} Budget
        </p>
        <p className="text-blue-100 mt-2">
          Activities: {itinerary.activity_type.split(',').map(activity => 
            activity.trim().charAt(0).toUpperCase() + activity.trim().slice(1)
          ).join(', ')}
        </p>
      </div>

      <div className="space-y-8">
        {days.map((day, dayIndex) => (
          <motion.div
            key={dayIndex}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: dayIndex * 0.1 }}
            className="bg-white rounded-lg shadow-lg overflow-hidden"
          >
            <div className="bg-gray-50 px-6 py-4">
              <h3 className="text-lg font-semibold">Day {day.dayNumber}</h3>
            </div>

            <div className="divide-y divide-gray-200">
              {day.activities.map((activity, activityIndex) => (
                <motion.div
                  key={activityIndex}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: (dayIndex * day.activities.length + activityIndex) * 0.05 }}
                  className="p-6 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start">
                    <div className="flex-shrink-0 w-24 text-sm font-medium text-gray-500">
                      {activity.time}
                    </div>
                    <div className="flex-1">
                      <h4 className="text-lg font-medium text-gray-900">{activity.description}</h4>
                      {activity.location && (
                        <p className="text-gray-500 mt-1">
                          📍 {activity.location}
                        </p>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default ItineraryDisplay;
