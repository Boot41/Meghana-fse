import React from 'react';
import { motion } from 'framer-motion';
import './Contact.css';

const Contact: React.FC = () => {
  return (
    <section className="contact-section" id="contact">
      <motion.div 
        className="contact-content"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <div className="contact-card">
          <h2>Email Us</h2>
          <div className="email-container">
            <a href="mailto:meghana@gmail.com" className="email-link">
              meghana@gmail.com
            </a>
          </div>
        </div>
      </motion.div>
    </section>
  );
};

export default Contact;
