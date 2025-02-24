import React from 'react';
import { useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import ChatBot from '../components/ChatBot/ChatBot';

const ChatPage: React.FC = () => {
  const location = useLocation();
  const searchQuery = location.state?.searchQuery;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="h-screen flex"
    >
      <div className="flex-1">
        <ChatBot />
      </div>
    </motion.div>
  );
};

export default ChatPage;
