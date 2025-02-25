import axios from 'axios';

// Log environment variables for debugging
console.log('Environment variables:', {
  VITE_APP_API_URL: import.meta.env.VITE_APP_API_URL,
  NODE_ENV: import.meta.env.MODE
});

// Backend API URL
const API_BASE_URL = import.meta.env.VITE_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: false  // Disable credentials for now
});

// Add request interceptor for debugging
api.interceptors.request.use(request => {
  console.log('🚀 Request:', {
    url: request.url,
    baseURL: request.baseURL,
    method: request.method,
    data: request.data,
    headers: request.headers
  });
  return request;
}, error => {
  console.error('❌ Request Error:', error);
  return Promise.reject(error);
});

// Add response interceptor for debugging
api.interceptors.response.use(
  response => {
    console.log('✅ Response:', {
      status: response.status,
      data: response.data,
      headers: response.headers
    });
    return response;
  },
  error => {
    // Handle network errors
    if (!error.response) {
      console.error('❌ Network Error:', error.message);
      return Promise.reject(new Error('Network error. Please check your connection.'));
    }

    // Handle API errors
    console.error('❌ Response Error:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      headers: error.response?.headers
    });
    return Promise.reject(error);
  }
);

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
  currentState: {
    state: string;
    data: any;
  };
  preferences: any;
  error?: string;
}

// Chat API endpoints
export const chatApi = {
  startChat: async (): Promise<ChatResponse> => {
    try {
      const response = await api.post('/api/chat/start/');
      return response.data;
    } catch (error) {
      console.error('Error in startChat:', error);
      throw error;
    }
  },

  sendMessage: async (message: string, preferences: any = {}, currentState: any = {}): Promise<ChatResponse> => {
    try {
      const response = await api.post('/api/chat/process/', {
        message,
        preferences,
        currentState
      });
      return response.data;
    } catch (error) {
      console.error('Error in sendMessage:', error);
      throw error;
    }
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
