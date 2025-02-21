import React, { useState, useEffect } from 'react';
import TravelForm from './components/TravelForm';
import Itinerary from './components/Itinerary';
import ChatInterface from './components/ChatInterface';
import './App.css';

function App() {
  const [itinerary, setItinerary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [backendStatus, setBackendStatus] = useState({ connected: false, message: '' });

  useEffect(() => {
    const checkBackend = async () => {
      try {
        console.log('Attempting to connect to backend...');
        const response = await fetch("http://localhost:8000/api/health/", {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Backend response:', data);
        
        setBackendStatus({
          connected: true,
          message: "Backend connected successfully!"
        });
      } catch (error) {
        console.error("Backend connection error:", error);
        setBackendStatus({
          connected: false,
          message: `Failed to connect to backend: ${error.message}`
        });
      }
    };
    
    checkBackend();
  }, []);

  const handleTravelRequest = async (formData) => {
    setLoading(true);
    setError(null);
    console.log('Submitting form data:', formData);
    
    try {
      // First, log the request details
      const requestBody = JSON.stringify(formData);
      console.log('Request body:', requestBody);
      
      const response = await fetch('http://localhost:8000/api/travel/plan/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: requestBody
      });
      
      console.log('Response status:', response.status);
      console.log('Response headers:', Object.fromEntries(response.headers.entries()));
      
      // Get the raw text first
      const rawText = await response.text();
      console.log('Raw response:', rawText);
      
      // Try to parse as JSON
      let responseData;
      try {
        responseData = JSON.parse(rawText);
        console.log('Parsed response data:', responseData);
      } catch (parseError) {
        console.error('Error parsing response:', parseError);
        throw new Error(`Server returned invalid JSON: ${rawText}`);
      }
      
      if (!response.ok) {
        throw new Error(responseData.error || 'Failed to generate itinerary');
      }
      
      setItinerary(responseData);
    } catch (err) {
      console.error('Error generating itinerary:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!backendStatus.connected) {
    return (
      <div className="App">
        <div className="connection-error">
          <h2>⚠️ Connection Error</h2>
          <p>{backendStatus.message}</p>
          <button onClick={() => window.location.reload()}>Retry Connection</button>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>✈️ AI Travel Planner</h1>
        <p className="subtitle">Your personal travel assistant powered by AI</p>
      </header>
      
      <main className="App-main">
        <div className="container">
          <div className="row">
            <div className="col-md-4">
              <div className="form-container">
                <h2>🎯 Plan Your Trip</h2>
                <TravelForm onSubmit={handleTravelRequest} disabled={loading} />
              </div>
            </div>
            
            <div className="col-md-8">
              {loading && (
                <div className="loading-spinner">
                  <div className="spinner"></div>
                  <p>🤖 AI is crafting your perfect itinerary...</p>
                </div>
              )}
              
              {error && (
                <div className="error-message">
                  <h3>⚠️ Oops!</h3>
                  <p>{error}</p>
                  <button onClick={() => setError(null)}>Try Again</button>
                </div>
              )}
              
              {itinerary && !loading && (
                <Itinerary data={itinerary} />
              )}
            </div>
          </div>
          
          <div className="row mt-4">
            <div className="col-12">
              <ChatInterface />
            </div>
          </div>
        </div>
      </main>

      <footer className="App-footer">
        <p>Powered by Groq LLM & OpenTripPlanner</p>
      </footer>
    </div>
  );
}

export default App;
