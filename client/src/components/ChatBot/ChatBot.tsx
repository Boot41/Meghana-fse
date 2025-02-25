import React, { useState, useRef, useEffect } from 'react';
import { chatApi } from '../../services/api';
import './ChatBot.css';

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

const ChatBot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [preferences, setPreferences] = useState({});
  const [currentState, setCurrentState] = useState({ state: 'initial' });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const initChat = async () => {
      try {
        setIsTyping(true);
        const response = await chatApi.startChat();
        console.log('Start chat response:', response);
        if (response.message) {
          addBotMessage(response.message);
        }
        if (response.currentState) {
          setCurrentState(response.currentState);
        }
        if (response.preferences) {
          setPreferences(response.preferences);
        }
      } catch (error) {
        console.error('Error starting chat:', error);
        addBotMessage('Hi! Where would you like to go?');
      } finally {
        setIsTyping(false);
      }
    };

    initChat();
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
    setIsTyping(true);

    try {
      const response = await chatApi.sendMessage(userMessage, preferences, currentState);
      console.log('Send message response:', response);
      
      if (response.currentState) {
        setCurrentState(response.currentState);
      }
      if (response.preferences) {
        setPreferences(response.preferences);
      }
      if (response.message) {
        addBotMessage(response.message);
      }
    } catch (error) {
      console.error('Error:', error);
      addBotMessage('Sorry, I encountered an error. Please try again.');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="chat-container">
      <div className="messages-container">
        {messages.map(msg => (
          <div key={msg.id} className={`message ${msg.sender}`}>
            <div className="message-content">{msg.text}</div>
            <div className="message-timestamp">
              {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
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
      <div className="input-area">
        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          rows={1}
        />
        <button onClick={handleSendMessage} disabled={!inputText.trim() || isTyping}>
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatBot;
