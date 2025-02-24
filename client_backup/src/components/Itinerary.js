import React from 'react';

function Itinerary({ data }) {
  if (!data || !data.days) {
    return null;
  }

  return (
    <div className="itinerary">
      <h2 className="itinerary-title">🗺️ Your Personalized Travel Plan</h2>
      
      {data.summary && (
        <div className="itinerary-summary">
          <h3>✨ Trip Overview</h3>
          <p>{data.summary}</p>
        </div>
      )}

      <div className="itinerary-days">
        {data.days.map((day, index) => (
          <div key={index} className="itinerary-day">
            <h3 className="day-header">
              Day {day.day_number}: {day.theme}
            </h3>
            
            <div className="day-activities">
              {day.activities.map((activity, actIndex) => (
                <div key={actIndex} className="activity-card">
                  <h4 className="activity-name">{activity.name}</h4>
                  
                  {activity.description && (
                    <p className="activity-description">{activity.description}</p>
                  )}
                  
                  <div className="activity-details">
                    {activity.duration && (
                      <span className="activity-duration">⏱️ {activity.duration}</span>
                    )}
                    {activity.cost_estimate && (
                      <span className="activity-cost">💰 {activity.cost_estimate}</span>
                    )}
                  </div>
                  
                  {activity.location && (
                    <div className="activity-location">
                      📍 {activity.location}
                    </div>
                  )}
                  
                  {activity.tips && activity.tips.length > 0 && (
                    <div className="activity-tips">
                      <h5>💡 Local Tips:</h5>
                      <ul>
                        {activity.tips.map((tip, tipIndex) => (
                          <li key={tipIndex}>{tip}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
      
      <div className="itinerary-actions">
        <button className="action-button">
          📱 Save to Mobile
        </button>
        <button className="action-button">
          🖨️ Print Itinerary
        </button>
        <button className="action-button">
          📩 Share via Email
        </button>
      </div>
    </div>
  );
}

export default Itinerary;
