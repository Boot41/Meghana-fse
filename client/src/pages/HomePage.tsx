import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import WeatherDisplay from '../components/Weather/WeatherDisplay';
import About from '../components/About/About';
import Contact from '../components/Contact/Contact';

const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-900 to-black text-white">
      <div className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <section className="hero">
            <div className="hero-content">
              <h1 className="text-4xl font-bold mb-6 text-center">Discover Your Next Adventure</h1>
              <p className="text-blue-200 mb-4 text-center">Plan your perfect trip with personalized recommendations and real-time weather updates.</p>
              <div className="text-center">
                <Link 
                  to="/chat" 
                  className="inline-block px-8 py-3 bg-blue-500 text-white rounded-full hover:bg-blue-600 transition-colors text-lg font-semibold shadow-lg hover:shadow-xl transform hover:-translate-y-1"
                >
                  Get Started
                </Link>
              </div>
            </div>
          </section>

          {/* Weather Section */}
          <div className="max-w-md mx-auto bg-blue-800/30 rounded-xl p-6 backdrop-blur-sm shadow-xl my-8">
            <h2 className="text-2xl font-semibold mb-4 text-center">Weather in Bangalore</h2>
            <WeatherDisplay location="Bangalore" />
          </div>

          <About />
          <Contact />

          {/* Quick Links */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="bg-blue-800/30 rounded-xl p-6 backdrop-blur-sm shadow-xl"
            >
              <h3 className="text-xl font-semibold mb-3">Plan Your Trip</h3>
              <p className="text-blue-200 mb-4">Get personalized travel recommendations using our AI-powered chat.</p>
              <Link to="/chat" className="inline-block bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors">
                Start Planning
              </Link>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default HomePage;
