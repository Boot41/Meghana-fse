import React, { useState, useEffect, useRef } from 'react';
import { chatApi, ChatResponse, DayPlan } from '../../services/api';
import './ChatInterface.css';

interface ChatInterfaceProps {
  onItineraryGenerated?: (itinerary: DayPlan[]) => void;
  initialMessage?: string;
}

interface Message {
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ onItineraryGenerated, initialMessage }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [currentState, setCurrentState] = useState<any>({
    state: 'initial',
    data: {}
  });
  const [preferences, setPreferences] = useState<any>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const initChat = async () => {
      try {
        const response = await chatApi.startChat();
        addBotMessage(initialMessage || response.message);
        if (response.currentState) {
          setCurrentState(response.currentState);
        }
        if (response.preferences) {
          setPreferences(response.preferences);
        }
      } catch (error) {
        console.error('Error starting chat:', error);
        addBotMessage(initialMessage || "Hi! Where would you like to go?");
      }
    };

    if (messages.length === 0) {
      initChat();
    }
    scrollToBottom();
  }, [messages, initialMessage]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const addMessage = (text: string, sender: 'user' | 'bot') => {
    setMessages(prev => [...prev, {
      text,
      sender,
      timestamp: new Date()
    }]);
  };

  const addBotMessage = async (text: string) => {
    setIsTyping(true);
    await new Promise(resolve => setTimeout(resolve, 500));
    addMessage(text, 'bot');
    setIsTyping(false);
  };

  const handleSend = async () => {
    if (!inputText.trim()) return;

    const userMessage = inputText.trim();
    addMessage(userMessage, 'user');
    setInputText('');
    setIsTyping(true);

    try {
      const response = await chatApi.sendMessage(userMessage, preferences, currentState);
      
      await addBotMessage(response.message);
      
      if (response.currentState) {
        setCurrentState(response.currentState);
      }
      
      if (response.preferences) {
        setPreferences(response.preferences);
      }

      if (response.currentState?.data?.itinerary && onItineraryGenerated) {
        onItineraryGenerated(response.currentState.data.itinerary);
      }
    } catch (error: any) {
      console.error('Error:', error);
      await addBotMessage("I'm sorry, I encountered an error. Please try again.");
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const formatTimestamp = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="chat-interface">
      <div className="messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`}>
            <div className="message-content">{msg.text}</div>
            <div className="message-timestamp">{formatTimestamp(msg.timestamp)}</div>
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
      <div className="input-area">
        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          rows={1}
        />
        <button onClick={handleSend} disabled={!inputText.trim() || isTyping}>
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;
