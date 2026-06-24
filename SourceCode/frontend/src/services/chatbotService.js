import api from '../utils/api';

const chatbotService = {
  /**
   * Send a chat message to the AI agent.
   * @param {string} message
   * @param {string} userId
   * @param {string} tripId  - currently selected trip (can be empty)
   */
  sendMessage: (message, userId, tripId = '') =>
    api.post('/chatbot/api/chat/', { message, user_id: userId, trip_id: tripId }),

  /** List all trips for a user (for trip selection in chatbot sidebar). */
  listTrips: (userId) => api.get(`/chatbot/api/trips/${userId}/`),

  /** Get full details + greeting for a selected trip. */
  getTrip: (tripId) => api.get(`/chatbot/api/trip/${tripId}/`),

  /** Clear in-memory conversation history. */
  clearMemory: (userId) =>
    api.delete(`/chatbot/api/memory/${userId}/`),

  /** Health check. */
  health: () => api.get('/chatbot/api/health/'),
};

export default chatbotService;
