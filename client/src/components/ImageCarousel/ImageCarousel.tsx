import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const images = [
  {
    url: 'https://images.unsplash.com/photo-1565967511849-76a60a516170',
    title: 'Santorini, Greece',
    description: 'Iconic white buildings and blue domes'
  },
  {
    url: 'https://images.unsplash.com/photo-1516483638261-f4dbaf036963',
    title: 'Tuscany, Italy',
    description: 'Rolling hills and cypress trees'
  },
  {
    url: 'https://images.unsplash.com/photo-1528164344705-47542687000d',
    title: 'Tokyo, Japan',
    description: 'Modern city lights and traditional culture'
  },
  {
    url: 'https://images.unsplash.com/photo-1512100356356-de1b84283e18',
    title: 'Machu Picchu, Peru',
    description: 'Ancient Incan citadel in the clouds'
  }
];

const ImageCarousel: React.FC = () => {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % images.length);
    }, 5000);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="relative h-[500px] overflow-hidden rounded-2xl">
      <AnimatePresence initial={false}>
        <motion.div
          key={currentIndex}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 1 }}
          className="absolute inset-0"
        >
          <div 
            className="absolute inset-0 bg-cover bg-center"
            style={{ 
              backgroundImage: `url(${images[currentIndex].url})`,
              filter: 'brightness(0.7)'
            }}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent" />
          <div className="absolute bottom-0 left-0 right-0 p-8 text-white">
            <h3 className="text-3xl font-bold mb-2">{images[currentIndex].title}</h3>
            <p className="text-lg">{images[currentIndex].description}</p>
          </div>
        </motion.div>
      </AnimatePresence>

      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex space-x-2">
        {images.map((_, index) => (
          <button
            key={index}
            className={`w-2 h-2 rounded-full transition-all ${
              index === currentIndex ? 'bg-white w-4' : 'bg-white/50'
            }`}
            onClick={() => setCurrentIndex(index)}
          />
        ))}
      </div>
    </div>
  );
};

export default ImageCarousel;
