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
      className="flex flex-col min-h-screen bg-gray-100"
    >
      <div className="flex-1 p-4 md:p-8">
        <div className="max-w-4xl mx-auto h-[80vh] bg-white rounded-lg shadow-lg overflow-hidden">
          <ChatBot />
        </div>
      </div>
    </motion.div>
  );
};

export default ChatPage;
