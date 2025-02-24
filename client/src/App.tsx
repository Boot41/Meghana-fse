import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import Header from './components/Layout/Header';
import ImageCarousel from './components/ImageCarousel/ImageCarousel';
import ChatPage from './pages/ChatPage';
import WeatherDisplay from './components/Weather/WeatherDisplay';
import About from './components/About/About';
import Contact from './components/Contact/Contact';
import Footer from './components/Footer/Footer';
import { motion } from 'framer-motion';

const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6, ease: "easeOut" }
};

const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1
    }
  }
};

function HomePage() {
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-b from-gray-900 to-gray-800">
      <Header />
      
      {/* Hero section with background image */}
      <div className="relative min-h-screen flex flex-col">
        {/* Image Carousel */}
        <div className="absolute inset-0">
          <ImageCarousel />
        </div>

        {/* Gradient overlay for better text visibility */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1.5 }}
          className="absolute inset-0 bg-gradient-to-b from-black/70 via-black/50 to-black/70"
        ></motion.div>

        {/* Content */}
        <div className="relative flex-1 flex flex-col items-center justify-start px-4 pt-40 pb-16">
          {/* Main animated section */}
          <motion.div 
            variants={staggerContainer}
            initial="initial"
            whileInView="animate"
            viewport={{ once: true, margin: "-100px" }}
            className="text-center max-w-4xl space-y-16 mb-16"
          >
            {/* Title and subtitle */}
            <motion.div variants={fadeInUp}>
              <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
                Your Travel Adventure Starts Here
              </h1>
              <p className="text-xl text-blue-200">
                Discover amazing destinations and create unforgettable memories
              </p>
            </motion.div>

            {/* Weather Display */}
            <motion.div variants={fadeInUp} className="max-w-md mx-auto">
              <div className="bg-black/30 backdrop-blur-sm rounded-xl p-6 shadow-xl">
                <h2 className="text-2xl font-semibold mb-4 text-white">Weather in Bangalore</h2>
                <WeatherDisplay location="Bangalore" />
              </div>
            </motion.div>

            {/* CTA Buttons */}
            <motion.div variants={fadeInUp} className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/plan"
                className="px-8 py-3 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-colors text-lg font-medium shadow-lg hover:shadow-xl"
              >
                Plan Your Trip
              </Link>
              <Link
                to="/chat"
                className="px-8 py-3 bg-purple-600 text-white rounded-full hover:bg-purple-700 transition-colors text-lg font-medium shadow-lg hover:shadow-xl"
              >
                Chat with AI
              </Link>
            </motion.div>
          </motion.div>

          {/* Features Section */}
          <motion.div 
            variants={staggerContainer}
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl w-full mt-16"
          >
            {/* AI Travel Planning */}
            <motion.div
              variants={fadeInUp}
              className="bg-white/5 backdrop-blur-sm rounded-xl p-6"
            >
              <div className="text-4xl mb-4">🤖</div>
              <h3 className="text-xl font-semibold mb-2">AI Travel Planning</h3>
              <p className="text-blue-200">
                Get personalized travel recommendations powered by advanced AI
              </p>
            </motion.div>

            {/* Real-time Weather */}
            <motion.div
              variants={fadeInUp}
              className="bg-white/5 backdrop-blur-sm rounded-xl p-6"
            >
              <div className="text-4xl mb-4">🌤</div>
              <h3 className="text-xl font-semibold mb-2">Real-time Weather</h3>
              <p className="text-blue-200">
                Stay updated with accurate weather forecasts for your destination
              </p>
            </motion.div>

            {/* Smart Suggestions */}
            <motion.div
              variants={fadeInUp}
              className="bg-white/5 backdrop-blur-sm rounded-xl p-6"
            >
              <div className="text-4xl mb-4">✨</div>
              <h3 className="text-xl font-semibold mb-2">Smart Suggestions</h3>
              <p className="text-blue-200">
                Get intelligent activity recommendations based on weather and preferences
              </p>
            </motion.div>
          </motion.div>
        </div>
      </div>
      <About />
      <Contact />
    </div>
  );
}

function App() {
  return (
    <Router>
      <div className="app">
        <Header />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/plan" element={<Navigate to="/chat" replace />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
