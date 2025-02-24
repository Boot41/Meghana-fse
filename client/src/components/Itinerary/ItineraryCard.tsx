import React from 'react';
import { CloudIcon, SunIcon, MoonIcon } from '@heroicons/react/24/outline';

interface Activity {
  time: string;
  name: string;
  location: string;
  description?: string;
  price?: string;
}

interface DayPlan {
  date: string;
  activities: Activity[];
  weather?: {
    condition: string;
    temperature: number;
    icon: string;
  };
}

export interface ItineraryCardProps {
  itinerary: DayPlan[];
}

const ItineraryCard: React.FC<ItineraryCardProps> = ({ itinerary }) => {
  const getTimeIcon = (time: string) => {
    const hour = parseInt(time.split(':')[0]);
    if (hour < 12) return <SunIcon className="w-5 h-5 text-yellow-500" />;
    if (hour < 18) return <CloudIcon className="w-5 h-5 text-blue-500" />;
    return <MoonIcon className="w-5 h-5 text-indigo-500" />;
  };

  return (
    <div className="space-y-8">
      {itinerary.map((day, dayIndex) => (
        <div key={dayIndex} className="bg-white rounded-xl shadow-md p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-semibold text-gray-900">
              Day {dayIndex + 1} - {day.date}
            </h3>
            {day.weather && (
              <div className="flex items-center gap-2 text-gray-600">
                <img src={day.weather.icon} alt={day.weather.condition} className="w-8 h-8" />
                <span>{day.weather.temperature}°C</span>
              </div>
            )}
          </div>
          
          <div className="space-y-4">
            {day.activities.map((activity, actIndex) => (
              <div
                key={actIndex}
                className="flex items-start gap-4 p-4 rounded-lg bg-gradient-to-r from-orange-50 to-rose-50"
              >
                <div className="flex-shrink-0">
                  {getTimeIcon(activity.time)}
                </div>
                <div className="flex-1">
                  <div className="flex justify-between">
                    <h4 className="font-medium text-gray-900">{activity.name}</h4>
                    <span className="text-gray-600">{activity.time}</span>
                  </div>
                  <p className="text-gray-600">{activity.location}</p>
                  {activity.description && (
                    <p className="text-gray-500 mt-1 text-sm">{activity.description}</p>
                  )}
                  {activity.price && (
                    <p className="text-gray-600 mt-1 text-sm">Estimated cost: {activity.price}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ItineraryCard;
