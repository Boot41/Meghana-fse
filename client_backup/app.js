// Main application logic
document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const startPlanningBtn = document.getElementById('startPlanningBtn');
    const chatInterface = document.getElementById('chatInterface');
    const chatHeader = document.getElementById('chatHeader');
    const chatMessages = document.getElementById('chatMessages');
    const messageInput = document.getElementById('messageInput');
    const sendMessage = document.getElementById('sendMessage');
    const itinerarySection = document.getElementById('itinerarySection');

    // State
    let chatOpen = false;
    let currentItinerary = null;
    let conversationState = {
        destination: null,
        duration: null,
        budget: null,
        interests: null
    };

    // Event Listeners
    startPlanningBtn.addEventListener('click', toggleChat);
    chatHeader.addEventListener('click', toggleChat);
    sendMessage.addEventListener('click', handleSendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSendMessage();
    });

    // Chat Toggle
    function toggleChat() {
        chatOpen = !chatOpen;
        chatInterface.style.transform = chatOpen ? 'translateY(0)' : 'translateY(100%)';
        if (chatOpen && !conversationState.destination) {
            setTimeout(() => addBotMessage("Hi! I'm your AI travel assistant. Where would you like to go?"), 500);
        }
    }

    // Message Handling
    async function handleSendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;

        addUserMessage(message);
        messageInput.value = '';

        // Process user input based on conversation state
        if (!conversationState.destination) {
            conversationState.destination = message;
            setTimeout(() => addBotMessage("Great choice! How many days would you like to spend there?"), 1000);
        } else if (!conversationState.duration) {
            conversationState.duration = parseInt(message);
            setTimeout(() => addBotMessage("What's your budget? (low, medium, or high)"), 1000);
        } else if (!conversationState.budget) {
            conversationState.budget = message.toLowerCase();
            setTimeout(() => addBotMessage("What are your interests? (e.g., food, history, adventure)"), 1000);
        } else if (!conversationState.interests) {
            conversationState.interests = message;
            await generateItinerary();
        }
    }

    // UI Helpers
    function addUserMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        messageDiv.textContent = text;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Add animation classes
        messageDiv.classList.add('message-enter');
        requestAnimationFrame(() => {
            messageDiv.classList.add('message-enter-active');
        });
    }

    function addBotMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message';
        messageDiv.textContent = text;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Add animation classes
        messageDiv.classList.add('message-enter');
        requestAnimationFrame(() => {
            messageDiv.classList.add('message-enter-active');
        });
    }

    // Itinerary Generation
    async function generateItinerary() {
        addBotMessage("Generating your personalized itinerary...");
        
        try {
            const response = await fetch('/api/generate-itinerary', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(conversationState)
            });

            const data = await response.json();
            currentItinerary = data;
            displayItinerary(data);
            
            addBotMessage("I've created your itinerary! You can view it below. Would you like to make any adjustments?");
        } catch (error) {
            console.error('Error generating itinerary:', error);
            addBotMessage("I'm sorry, there was an error generating your itinerary. Please try again.");
        }
    }

    // Itinerary Display
    function displayItinerary(itinerary) {
        itinerarySection.classList.remove('hidden');
        const content = document.getElementById('itineraryContent');
        content.innerHTML = '';

        itinerary.forEach((day, index) => {
            const daySection = document.createElement('div');
            daySection.className = 'day-section mb-8 p-6 bg-white rounded-lg shadow-md';
            
            // Day header with weather
            const header = document.createElement('div');
            header.className = 'flex items-center justify-between mb-4';
            header.innerHTML = `
                <h3 class="text-xl font-semibold text-gray-800">Day ${index + 1}</h3>
                <div class="flex items-center space-x-2">
                    <img src="${day.weather.icon}" alt="weather" class="w-8 h-8 weather-icon">
                    <span class="text-gray-600">${day.weather.temp}°C</span>
                </div>
            `;
            daySection.appendChild(header);

            // Activities
            day.activities.forEach(activity => {
                const activityCard = document.createElement('div');
                activityCard.className = 'activity-card bg-gray-50 rounded-lg p-4 mb-4';
                activityCard.innerHTML = `
                    <div class="flex justify-between items-start">
                        <div>
                            <p class="font-medium text-gray-800">${activity.time} - ${activity.name}</p>
                            <p class="text-gray-600 text-sm">${activity.location}</p>
                        </div>
                        <span class="price-tag">${activity.price}</span>
                    </div>
                    ${activity.note ? `<p class="text-gray-500 text-sm mt-2">${activity.note}</p>` : ''}
                `;
                daySection.appendChild(activityCard);
            });

            content.appendChild(daySection);
        });

        // Scroll to itinerary
        itinerarySection.scrollIntoView({ behavior: 'smooth' });
    }
});
