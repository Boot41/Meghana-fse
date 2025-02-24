import React from 'react';
import { motion } from 'framer-motion';
import './About.css';

const About: React.FC = () => {
  return (
    <section className="about-section" id="about">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="about-content"
      >
        <h2>About Us</h2>
        <p>Welcome to your premier travel companion! We're passionate about making your travel experiences unforgettable.</p>
        
        <div className="about-features">
          <div className="feature">
            <h3>Expert Planning</h3>
            <p>Our AI-powered system helps create personalized travel itineraries tailored to your preferences.</p>
          </div>
          
          <div className="feature">
            <h3>Real-Time Weather</h3>
            <p>Stay informed with up-to-date weather information for your destination.</p>
          </div>
          
          <div className="feature">
            <h3>Local Insights</h3>
            <p>Get authentic recommendations and insights about your destination.</p>
          </div>
        </div>
      </motion.div>
    </section>
  );
};

export default About;
