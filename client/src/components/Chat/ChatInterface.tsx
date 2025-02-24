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
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const initChat = async () => {
      try {
        const response = await chatApi.startChat();
        addBotMessage(initialMessage || response.data.message);
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
      const response = await chatApi.sendMessage(userMessage, currentState.data);
      const data = response.data;
      
      await addBotMessage(data.message);
      
      if (data.currentState) {
        setCurrentState(data.currentState);
      }

      if (data.itinerary && onItineraryGenerated) {
        onItineraryGenerated(data.itinerary);
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
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.sender}`}>
            <div className="message-content">
              {message.text}
            </div>
            <div className="message-timestamp">
              {formatTimestamp(message.timestamp)}
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="message bot">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="input-container">
        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          rows={1}
          autoFocus
        />
        <button onClick={handleSend} disabled={!inputText.trim() || isTyping}>
          {isTyping ? 'Thinking...' : 'Send'}
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;
