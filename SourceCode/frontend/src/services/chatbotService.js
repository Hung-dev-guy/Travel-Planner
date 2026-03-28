import api from '../utils/api';

const chatbotService = {
  sendMessage: (message) => api.post('/chatbot', { message }),
  getHistory: () => api.get('/chatbot/history'),
};

export default chatbotService;
