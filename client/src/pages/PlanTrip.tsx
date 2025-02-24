import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { chatApi, ChatResponse } from '../services/api';

interface ChatMessage {
  text: string;
  sender: 'user' | 'ai';
}

const PlanTrip: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [currentState, setCurrentState] = useState<any>({
    state: 'initial',
    data: {}
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize chat when component mounts
  useEffect(() => {
    const initializeChat = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await chatApi.startChat();
        console.log('Start chat response:', response);
        setChatHistory([{ text: response.data.message, sender: 'ai' }]);
        setCurrentState(response.data.currentState);
      } catch (error: any) {
        console.error('Error initializing chat:', error);
        const errorMessage = error.response?.data?.message || error.message || 'Failed to initialize chat';
        setError(errorMessage);
        setChatHistory([{ 
          text: 'Hi! I can help you plan your perfect trip. Where would you like to go?', 
          sender: 'ai' 
        }]);
      } finally {
        setIsLoading(false);
      }
    };

    initializeChat();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || isLoading) return;

    // Add user message to chat history
    setChatHistory(prev => [...prev, { text: inputText, sender: 'user' }]);
    setIsLoading(true);

    try {
      const response = await chatApi.sendMessage(inputText.trim(), currentState.data);
      
      // Update state and show AI response
      setCurrentState(response.data.currentState);
      setChatHistory(prev => [...prev, { text: response.data.message, sender: 'ai' }]);

      // If we have a complete itinerary, show it
      if (response.data.itinerary) {
        const itineraryText = formatItinerary(response.data);
        setChatHistory(prev => [...prev, { text: itineraryText, sender: 'ai' }]);
      }
    } catch (error: any) {
      console.error('Error:', error);
      const errorMessage = error.response?.data?.message || error.message || 'Failed to send message';
      setError(errorMessage);
      setChatHistory(prev => [...prev, { 
        text: "I'm sorry, I encountered an error while processing your request. Please try again.", 
        sender: 'ai' 
      }]);
    } finally {
      setInputText('');
      setIsLoading(false);
    }
  };

  const formatItinerary = (data: ChatResponse): string => {
    let text = "Here's your travel itinerary:\n\n";
    
    if (data.summary) {
      text += `${data.summary}\n\n`;
    }

    if (data.itinerary) {
      data.itinerary.forEach(day => {
        text += `Day ${day.day}:\n`;
        day.activities.forEach(activity => {
          text += `${activity.time}: ${activity.name} - ${activity.description}\n`;
          if (activity.weather_note) {
            text += `Weather note: ${activity.weather_note}\n`;
          }
        });
        text += '\n';
      });
    }

    if (data.tips && data.tips.length > 0) {
      text += '\nTravel Tips:\n';
      data.tips.forEach(tip => {
        text += `- ${tip}\n`;
      });
    }

    if (data.weather_summary) {
      text += `\nWeather Summary: ${data.weather_summary}\n`;
    }

    return text;
  };

  return (
    <div className="min-h-screen">
      <div className="container mx-auto px-4 py-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="relative max-w-5xl mx-auto flex flex-col bg-black/20 backdrop-blur-xl rounded-3xl border border-white/10 shadow-2xl overflow-hidden"
          style={{ minHeight: 'calc(100vh - 48px)' }}
        >
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 text-red-500 px-4 py-2 mb-4 rounded">
              {error}
            </div>
          )}
          
          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {chatHistory.map((msg, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'} items-end space-x-2`}
              >
                {msg.sender === 'ai' && (
                  <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-white text-sm font-bold">
                    AI
                  </div>
                )}
                <div
                  className={`max-w-[80%] p-4 ${
                    msg.sender === 'user'
                      ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg rounded-2xl rounded-tr-sm'
                      : 'bg-white/10 text-white border border-white/10 rounded-2xl rounded-tl-sm'
                  }`}
                >
                  {msg.text.split('\n').map((line, i) => (
                    <p key={i} className="text-sm md:text-base">{line}</p>
                  ))}
                </div>
              </motion.div>
            ))}
            {isLoading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex justify-start items-end space-x-2"
              >
                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-white text-sm font-bold">
                  AI
                </div>
                <div className="bg-white/10 border border-white/10 p-4 rounded-2xl rounded-tl-sm text-white">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              </motion.div>
            )}
          </div>

          {/* Message Input */}
          <div className="p-4 border-t border-white/10 bg-gradient-to-r from-blue-500/10 to-purple-600/10">
            <form onSubmit={handleSubmit} className="flex space-x-4">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Where would you like to travel? I'll help plan your trip..."
                className="flex-1 px-4 py-3 bg-black/20 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 transition-colors"
                autoFocus
              />
              <button
                type="submit"
                disabled={!inputText.trim() || isLoading}
                className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-semibold hover:from-blue-600 hover:to-purple-700 transition-all duration-300 transform hover:-translate-y-0.5 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0 flex items-center justify-center min-w-[100px]"
              >
                {isLoading ? (
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                ) : (
                  <span className="flex items-center">
                    Send
                    <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                    </svg>
                  </span>
                )}
              </button>
            </form>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default PlanTrip;
