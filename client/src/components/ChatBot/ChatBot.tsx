import React, { useState, useRef, useEffect } from 'react';
import { chatApi } from '../../services/api';
import './ChatBot.css';

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

const INITIAL_MESSAGE = "Hi! I'm your AI travel assistant. Where would you like to go?";

const ChatBot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Add initial message when component mounts
    if (messages.length === 0) {
      addBotMessage(INITIAL_MESSAGE);
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
    addMessage(text, 'bot');
  };

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;

    const userMessage = inputText.trim();
    setInputText('');
    addMessage(userMessage, 'user');

    try {
      setIsTyping(true);
      console.log('Sending message:', userMessage);
      const response = await chatApi.sendMessage(userMessage);
      console.log('Got response:', response);
      
      if (response.reply) {
        // Add a small delay to simulate typing
        await new Promise(resolve => setTimeout(resolve, 1000));
        addMessage(response.reply, 'bot');
      }
      
      if (response.data?.itinerary) {
        await new Promise(resolve => setTimeout(resolve, 500));
        addMessage(response.data.itinerary, 'bot');
      }
      
    } catch (error) {
      console.error('Error sending message:', error);
      addMessage("I apologize, but I encountered an error while processing your request. Please try again.", 'bot');
    } finally {
      setIsTyping(false);
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
