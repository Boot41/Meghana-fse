import React, { useState, useRef, useEffect } from 'react';
import { chatApi } from '../../services/api';
import './ChatBot.css';

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

interface TravelPreferences {
  destination?: string;
  days?: number;
  budget?: string;
  interests?: string[];
}

interface WeatherOverview {
  condition: string;
  temperature: string;
  recommendation: string;
}

interface Activity {
  time: string;
  description: string;
  location: string;
  weather_note?: string;
  attire?: string;
}

interface DayPlan {
  day: number;
  weather_overview: WeatherOverview;
  activities: Activity[];
}

interface TravelPlan {
  itinerary: DayPlan[];
  summary?: string;
  tips: string[];
  weather_summary: string;
}

const ChatBot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [currentState, setCurrentState] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const initChat = async () => {
      try {
        const response = await chatApi.startChat();
        addBotMessage(response.reply);
        setCurrentState(response.state);
      } catch (error) {
        console.error('Error starting chat:', error);
        addBotMessage("I apologize, but I encountered an error. Please try again.");
      }
    };

    if (messages.length === 0) {
      initChat();
    }
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const addMessage = (text: string, sender: 'user' | 'bot') => {
    setMessages(prev => [...prev, {
      id: Date.now(),
      text,
      sender,
      timestamp: new Date()
    }]);
  };

  const addBotMessage = (text: string) => {
    setIsTyping(true);
    setTimeout(() => {
      addMessage(text, 'bot');
      setIsTyping(false);
    }, 500);
  };

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;

    const userMessage = inputText.trim();
    setInputText('');
    addMessage(userMessage, 'user');

    try {
      setIsTyping(true);
      const history = messages.map(msg => ({
        type: msg.sender === 'user' ? 'user' : 'assistant',
        content: msg.text
      }));

      const response = await chatApi.sendMessage(userMessage, currentState, history);
      setCurrentState(response.state);
      addBotMessage(response.reply);
    } catch (error) {
      console.error('Error sending message:', error);
      addBotMessage("I apologize, but I encountered an error while processing your request. Please try again.");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="chatbot-container">
      <div className="chat-messages">
        {messages.map(message => (
          <div key={message.id} className={`message ${message.sender}`}>
            <div className="message-content">
              {message.text}
            </div>
            <div className="message-timestamp">
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="message bot">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input">
        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          rows={1}
        />
        <button onClick={handleSendMessage} disabled={!inputText.trim()}>
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatBot;
