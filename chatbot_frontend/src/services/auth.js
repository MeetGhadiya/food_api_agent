class AuthService {
  constructor() {
    this.TOKEN_KEY = 'food_delivery_token';
    this.USER_KEY = 'food_delivery_user';
  }

  setAuth(token, username) {
    localStorage.setItem(this.TOKEN_KEY, token);
    localStorage.setItem(this.USER_KEY, username);
  }

  getToken() {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  getUser() {
    return localStorage.getItem(this.USER_KEY);
  }

  isAuthenticated() {
    return !!this.getToken();
  }

  logout() {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
  }

  clearAll() {
    localStorage.clear();
  }
}

export default new AuthService();
