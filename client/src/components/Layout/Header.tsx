import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Header: React.FC = () => {
  const location = useLocation();
  const isHomePage = location.pathname === '/' || location.pathname === '';
  const isChatPage = location.pathname === '/plan';

  if (isChatPage) return null;

  return (
    <header className="fixed top-0 left-0 right-0 bg-gradient-to-r from-black/50 to-black/40 backdrop-blur-xl border-b border-white/20 z-50 shadow-lg" style={{ height: '70px' }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-full">
        <div className="flex items-center justify-between h-full">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center shadow-lg">
              <span className="text-2xl font-bold text-white">P</span>
            </div>
            <span className="text-3xl font-extrabold bg-gradient-to-r from-blue-400 to-purple-400 text-transparent bg-clip-text animate-gradient">
              Planora
            </span>
          </Link>

          {/* Navigation */}
          <nav className="flex items-center space-x-8">
            <Link to="/" className="text-white font-medium hover:text-blue-300 transition-colors">Home</Link>
            <Link to="/plan" className="text-white font-medium hover:text-blue-300 transition-colors">Plan Trip</Link>
            <a 
              href="#about" 
              className="text-white font-medium hover:text-blue-300 transition-colors cursor-pointer"
              onClick={(e) => {
                e.preventDefault();
                document.getElementById('about')?.scrollIntoView({ behavior: 'smooth' });
              }}
            >
              About
            </a>
            <a 
              href="#contact" 
              className="text-white font-medium hover:text-blue-300 transition-colors cursor-pointer"
              onClick={(e) => {
                e.preventDefault();
                document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' });
              }}
            >
              Contact
            </a>
            {isHomePage && (
              <Link
                to="/plan"
                className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-full hover:from-blue-600 hover:to-purple-700 transition-all duration-300 transform hover:-translate-y-0.5"
              >
                Get Started
              </Link>
            )}
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;
