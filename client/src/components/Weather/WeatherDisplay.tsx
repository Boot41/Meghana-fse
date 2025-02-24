import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import './WeatherDisplay.css';

interface WeatherDisplayProps {
  location: string;
}

interface WeatherData {
  temp_c: number;
  condition: {
    text: string;
    icon: string;
  };
  humidity: number;
  wind_kph: number;
  wind_dir: string;
  feelslike_c: number;
  uv: number;
  last_updated: string;
}

// Map weather conditions to emoji icons
const weatherIcons: { [key: string]: string } = {
  'clear': '☀️',
  'sunny': '☀️',
  'partly cloudy': '⛅',
  'cloudy': '☁️',
  'overcast': '☁️',
  'mist': '🌫️',
  'rain': '🌧️',
  'light rain': '🌦️',
  'heavy rain': '⛈️',
  'thunder': '⛈️',
  'snow': '🌨️',
  'default': '☀️'
};

const getWeatherIcon = (condition: string): string => {
  const lowerCondition = condition.toLowerCase();
  return Object.entries(weatherIcons).find(([key]) => lowerCondition.includes(key))?.[1] || weatherIcons.default;
};

const getActivitySuggestion = (weather: WeatherData) => {
  const condition = weather.condition.text.toLowerCase();
  const temp = weather.temp_c;
  
  let message = '';
  let activities = '';
  
  if (condition.includes('rain') || condition.includes('thunder')) {
    message = 'Indoor activities recommended.';
    activities = 'Visit museums, cafes, or shopping malls.';
  } else if (temp > 30) {
    message = 'High temperature alert!';
    activities = 'Stay hydrated and prefer indoor activities.';
  } else if (temp < 15) {
    message = 'It\'s a bit chilly!';
    activities = 'Bring warm clothes and enjoy outdoor activities.';
  } else if (condition.includes('clear') || condition.includes('sunny')) {
    message = 'Perfect weather for outdoor activities!';
    activities = 'Try sightseeing, parks, or outdoor dining.';
  } else {
    message = 'Moderate weather conditions.';
    activities = 'Good for most outdoor and indoor activities.';
  }
  
  return { message, activities };
};

const WeatherDisplay: React.FC<WeatherDisplayProps> = ({ location }) => {
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchWeather = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const url = `http://localhost:8000/api/weather/${encodeURIComponent(location)}`;
        console.log('🌤 Fetching weather from:', url);
        
        const response = await axios.get(url);
        console.log('📥 Weather response:', response.data);
        
        if (response.data.error) {
          throw new Error(response.data.error);
        }

        const currentWeather = response.data.current;
        if (!currentWeather) {
          throw new Error('No weather data available');
        }

        setWeather({
          temp_c: currentWeather.temp_c,
          condition: currentWeather.condition,
          humidity: currentWeather.humidity,
          wind_kph: currentWeather.wind_kph,
          wind_dir: currentWeather.wind_dir,
          feelslike_c: currentWeather.feelslike_c,
          uv: currentWeather.uv,
          last_updated: currentWeather.last_updated,
        });
      } catch (err) {
        console.error('❌ Weather fetch error:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch weather data');
      } finally {
        setLoading(false);
      }
    };

    fetchWeather();
    // Refresh weather data every 5 minutes
    const interval = setInterval(fetchWeather, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [location]);

  if (loading) {
    return (
      <div className="weather-loading">
        <div className="loading-spinner"></div>
        <p>Loading weather data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="weather-error">
        <p>❌ {error}</p>
        <button onClick={() => window.location.reload()} className="retry-button">
          Retry
        </button>
      </div>
    );
  }

  if (!weather) {
    return (
      <div className="weather-error">
        <p>No weather data available</p>
      </div>
    );
  }

  const { message, activities } = getActivitySuggestion(weather);

  return (
    <motion.div 
      className="weather-display"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="weather-main">
        <div className="weather-temp">
          <span className="temp-value">{Math.round(weather.temp_c)}°C</span>
          <span className="weather-icon">{getWeatherIcon(weather.condition.text)}</span>
        </div>
        <div className="weather-condition">
          {weather.condition.text}
        </div>
      </div>
      
      <div className="weather-details">
        <div className="detail-item">
          <span className="detail-label">Feels like</span>
          <span className="detail-value">{Math.round(weather.feelslike_c)}°C</span>
        </div>
        <div className="detail-item">
          <span className="detail-label">Humidity</span>
          <span className="detail-value">{weather.humidity}%</span>
        </div>
        <div className="detail-item">
          <span className="detail-label">Wind</span>
          <span className="detail-value">{Math.round(weather.wind_kph)} km/h {weather.wind_dir}</span>
        </div>
      </div>
      
      <div className="weather-updated">
        Last updated: {new Date(weather.last_updated).toLocaleTimeString()}
      </div>
      
      <div className="weather-activity">
        <div className="activity-message">{message}</div>
        <div className="activity-suggestion">{activities}</div>
      </div>
    </motion.div>
  );
};

export default WeatherDisplay;
