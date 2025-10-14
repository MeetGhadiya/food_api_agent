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

  /**
   * Send a message to the AI chatbot agent.
   * 
   * PHASE 1.1: SEAMLESS SINGLE SIGN-ON IMPLEMENTATION
   * 
   * This function now automatically reads the JWT token from localStorage
   * and includes it in BOTH the request body AND the Authorization header.
   * 
   * This enables the agent to:
   * 1. Recognize the user is already authenticated on the website
   * 2. Skip the redundant login step in the chat
   * 3. Immediately proceed with authenticated actions (orders, etc.)
   * 
   * @param {string} message - The user's chat message
   * @param {string} userId - User identifier (default: 'guest')
   * @param {string|null} token - Optional token (will auto-read from localStorage if not provided)
   * @returns {Promise<Object>} The agent's response
   */
  async sendMessage(message, userId = 'guest', token = null) {
    try {
      // CRITICAL: Auto-read token from localStorage if not explicitly provided
      // This is where the "seamless" part happens - no manual token passing needed!
      const storedToken = token || localStorage.getItem('token');
      
      // Build the request payload
      const payload = {
        message,
        user_id: userId,
      };

      // Include token in payload for backward compatibility
      if (storedToken) {
        payload.token = storedToken;
      }

      // Build headers - INCLUDE Authorization header for seamless auth
      const headers = {
        'Content-Type': 'application/json',
      };

      // PHASE 1.1 KEY CHANGE: Add Authorization header if token exists
      // This allows the Flask agent to extract it from the request header
      // instead of requiring it in every tool call
      if (storedToken) {
        headers['Authorization'] = `Bearer ${storedToken}`;
      }

      console.log('🔐 Sending message with authentication:', {
        hasToken: !!storedToken,
        hasAuthHeader: !!headers['Authorization'],
        userId,
      });

      const response = await this.client.post('/chat', payload, { headers });
      
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
