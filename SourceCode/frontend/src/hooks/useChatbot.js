import { useState } from 'react';
import chatbotService from '../services/chatbotService';

const useChatbot = () => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async (text) => {
    setLoading(true);
    try {
      const res = await chatbotService.sendMessage(text);
      setMessages((prev) => [...prev, { text, sender: 'user' }, { text: res.data.reply, sender: 'bot' }]);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return { messages, loading, sendMessage };
};

export default useChatbot;
