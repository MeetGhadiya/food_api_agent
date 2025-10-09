import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';

class ChatAPI {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async sendMessage(message, userId = 'guest', token = null) {
    try {
      const response = await this.client.post('/chat', {
        message,
        user_id: userId,
        token,
      });
      return response.data;
    } catch (error) {
      console.error('Chat API Error:', error);
      throw error;
    }
  }

  async checkHealth() {
    try {
      const response = await this.client.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health Check Error:', error);
      throw error;
    }
  }

  async clearSession(userId) {
    try {
      const response = await this.client.post('/clear-session', {
        user_id: userId,
      });
      return response.data;
    } catch (error) {
      console.error('Clear Session Error:', error);
      throw error;
    }
  }
}

export default new ChatAPI();
