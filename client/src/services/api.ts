import axios from 'axios';

// Log environment variables for debugging
console.log('Environment variables:', {
  REACT_APP_API_URL: process.env.REACT_APP_API_URL,
  NODE_ENV: process.env.NODE_ENV
});

// Backend API URL
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
  console.log('🚀 Request:', {
    url: request.url,
    baseURL: request.baseURL,
    method: request.method,
    data: request.data,
    headers: request.headers
  });
  return request;
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
    console.error('❌ Error:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      headers: error.response?.headers
    });
    throw error;
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
  reply: string;
  state: string;
  data: any;
  error?: string;
}

// Chat API endpoints
export const chatApi = {
  sendMessage: async (message: string): Promise<ChatResponse> => {
    try {
      console.log('📤 Sending message:', message);
      const response = await api.post<ChatResponse>('/api/chat/', { message });
      console.log('📥 Received response:', response.data);
      return response.data;
    } catch (error) {
      console.error('💥 Error sending message:', error);
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
