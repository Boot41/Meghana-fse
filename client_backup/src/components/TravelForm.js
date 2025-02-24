import React, { useState } from 'react';

function TravelForm({ onSubmit, disabled }) {
  const [formData, setFormData] = useState({
    destination: '',
    duration: '',
    budget: 'medium',
    interests: [],
    dates: '',
    style: 'balanced'
  });

  const interests = [
    'Culture & History',
    'Food & Cuisine',
    'Nature & Outdoors',
    'Shopping',
    'Adventure',
    'Relaxation',
    'Nightlife',
    'Art & Museums'
  ];

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    if (type === 'checkbox') {
      setFormData(prev => ({
        ...prev,
        interests: checked 
          ? [...prev.interests, value]
          : prev.interests.filter(interest => interest !== value)
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="travel-form">
      <div className="form-group">
        <label htmlFor="destination">Where do you want to go? 🌎</label>
        <input
          type="text"
          id="destination"
          name="destination"
          value={formData.destination}
          onChange={handleChange}
          required
          placeholder="e.g., Paris, Tokyo, New York"
          className="form-control"
        />
      </div>

      <div className="form-group">
        <label htmlFor="duration">How long is your trip? ⏱️</label>
        <input
          type="number"
          id="duration"
          name="duration"
          value={formData.duration}
          onChange={handleChange}
          required
          min="1"
          max="30"
          placeholder="Number of days"
          className="form-control"
        />
      </div>

      <div className="form-group">
        <label htmlFor="budget">What's your budget level? 💰</label>
        <select
          id="budget"
          name="budget"
          value={formData.budget}
          onChange={handleChange}
          className="form-control"
        >
          <option value="budget">Budget-friendly</option>
          <option value="medium">Moderate</option>
          <option value="luxury">Luxury</option>
        </select>
      </div>

      <div className="form-group">
        <label>What are your interests? 🎯</label>
        <div className="interests-grid">
          {interests.map(interest => (
            <div key={interest} className="interest-item">
              <input
                type="checkbox"
                id={interest}
                name="interests"
                value={interest}
                checked={formData.interests.includes(interest)}
                onChange={handleChange}
              />
              <label htmlFor={interest}>{interest}</label>
            </div>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="dates">When are you planning to travel? 📅</label>
        <input
          type="date"
          id="dates"
          name="dates"
          value={formData.dates}
          onChange={handleChange}
          className="form-control"
        />
      </div>

      <div className="form-group">
        <label htmlFor="style">What's your preferred travel style? 🎨</label>
        <select
          id="style"
          name="style"
          value={formData.style}
          onChange={handleChange}
          className="form-control"
        >
          <option value="relaxed">Relaxed & Easy-going</option>
          <option value="balanced">Balanced Mix</option>
          <option value="active">Active & Adventurous</option>
        </select>
      </div>

      <button 
        type="submit" 
        className="submit-button" 
        disabled={disabled}
      >
        {disabled ? 'Generating...' : 'Plan My Trip! 🚀'}
      </button>
    </form>
  );
}

export default TravelForm;
