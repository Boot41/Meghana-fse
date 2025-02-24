import axios from 'axios';

// Log environment variables for debugging
console.log('Environment variables:', {
  REACT_APP_API_URL: process.env.REACT_APP_API_URL,
  NODE_ENV: process.env.NODE_ENV
});

// Hardcode the base URL for now to debug
const API_BASE_URL = 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: false
});

// Add request interceptor for debugging
api.interceptors.request.use(request => {
  console.log('Request:', {
    url: request.url,
    baseURL: request.baseURL,
    method: request.method,
    data: request.data
  });
  return request;
});

// Interface definitions
interface Activity {
  time: string;
  name: string;
  description: string;
  type: string;
  weather_note: string;
}

interface DayPlan {
  day: number;
  activities: Activity[];
  weather: {
    condition: string;
    temperature: number;
    humidity: number;
    wind_speed: number;
  };
}

interface TravelPlan {
  itinerary: DayPlan[];
  summary: string;
  tips: string[];
  weather_summary: string;
}

interface TravelPreferences {
  destination?: string;
  days?: number;
  budget?: string;
  interests?: string[];
}

interface ChatMessage {
  message: string;
  preferences?: TravelPreferences;
  currentState?: {
    state: string;
    data: any;
  };
  itinerary?: DayPlan[];
  summary?: string;
  tips?: string[];
  weather_summary?: string;
  weather?: any;
}

interface ChatResponse {
  message: string;
  preferences?: TravelPreferences;
  currentState?: {
    state: string;
    data: any;
  };
  itinerary?: DayPlan[];
  summary?: string;
  tips?: string[];
  weather_summary?: string;
  weather?: any;
}

// Chat API endpoints
export const chatApi = {
  startChat: async (): Promise<ChatResponse> => {
    const response = await api.post('/api/chat/start/');
    return response.data;
  },

  sendMessage: async (
    message: string,
    state: string = '',
    history: Array<{type: string, content: string}> = []
  ): Promise<ChatResponse> => {
    const response = await api.post('/api/chat/process/', {
      message,
      state,
      history
    });
    return response.data;
  },

  sendItineraryEmail: async (email: string, itinerary: any): Promise<any> => {
    const response = await api.post('/api/chat/send-email/', {
      email,
      itinerary
    });
    return response.data;
  }
};

export default api;

// Export interfaces for use in other components
export type {
  Activity,
  DayPlan,
  TravelPlan,
  TravelPreferences,
  ChatMessage,
  ChatResponse
};
