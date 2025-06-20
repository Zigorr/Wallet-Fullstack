// Global state manager for login form that persists across component unmounts
class LoginFormStateManager {
  private username: string = '';
  private password: string = '';
  private initialized: boolean = false;

  constructor() {
    this.loadFromStorage();
  }

  private loadFromStorage() {
    if (typeof window !== 'undefined') {
      this.username = sessionStorage.getItem('login_form_username') || '';
      this.password = sessionStorage.getItem('login_form_password') || '';
      this.initialized = true;
    }
  }

  getUsername(): string {
    if (!this.initialized) this.loadFromStorage();
    return this.username;
  }

  getPassword(): string {
    if (!this.initialized) this.loadFromStorage();
    return this.password;
  }

  setUsername(value: string) {
    this.username = value;
    if (typeof window !== 'undefined') {
      sessionStorage.setItem('login_form_username', value);
    }
  }

  setPassword(value: string) {
    this.password = value;
    if (typeof window !== 'undefined') {
      sessionStorage.setItem('login_form_password', value);
    }
  }

  clear() {
    this.username = '';
    this.password = '';
    if (typeof window !== 'undefined') {
      sessionStorage.removeItem('login_form_username');
      sessionStorage.removeItem('login_form_password');
    }
  }
}

// Create a singleton instance
export const loginFormState = new LoginFormStateManager(); 