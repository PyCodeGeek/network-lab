// assets/js/auth.js - Authentication Manager

class AuthManager {
    constructor() {
        this.user = null;
        this.listeners = [];
        this.isInitialized = false;
        this.loginAttempts = 0;
        this.maxLoginAttempts = 5;
        this.lockoutTime = 15 * 60 * 1000; // 15 minutes
    }

    /**
     * Initialize authentication manager
     */
    async init() {
        if (this.isInitialized) return;

        // Check for existing session
        await this.checkAuth();
        
        // Set up token refresh timer
        this.setupTokenRefresh();
        
        // Listen for storage changes (multi-tab support)
        this.setupStorageListener();
        
        this.isInitialized = true;
        console.log('Auth manager initialized');
    }

    /**
     * Add authentication state listener
     */
    addListener(callback) {
        this.listeners.push(callback);
    }

    /**
     * Remove authentication state listener
     */
    removeListener(callback) {
        this.listeners = this.listeners.filter(l => l !== callback);
    }

    /**
     * Notify all listeners of authentication state change
     */
    notifyListeners() {
        this.listeners.forEach(callback => {
            try {
                callback(this.user);
            } catch (error) {
                console.error('Auth listener error:', error);
            }
        });
    }

    /**
     * Check if user is currently authenticated
     */
    isAuthenticated() {
        return !!this.user && !!api.token;
    }

    /**
     * Get current user
     */
    getUser() {
        return this.user;
    }

    /**
     * Get user role
     */
    getUserRole() {
        return this.user?.role || 'guest';
    }

    /**
     * Check if user has specific permission
     */
    hasPermission(permission) {
        if (!this.user) return false;
        
        const rolePermissions = {
            admin: ['read', 'write', 'delete', 'manage_users', 'manage_system'],
            operator: ['read', 'write', 'provision', 'monitor'],
            viewer: ['read', 'monitor'],
            guest: []
        };

        const userPermissions = rolePermissions[this.user.role] || [];
        return userPermissions.includes(permission);
    }

    /**
     * Check current authentication status
     */
    async checkAuth() {
        const token = getLocalStorage('auth_token');
        
        if (!token) {
            this.user = null;
            this.notifyListeners();
            return false;
        }

        try {
            const profile = await api.getProfile();
            this.user = profile;
            this.notifyListeners();
            return true;
        } catch (error) {
            console.log('Auth check failed:', error.message);
            this.logout();
            return false;
        }
    }

    /**
     * Perform user login
     */
    async login(username, password) {
        // Check for account lockout
        if (this.isAccountLocked()) {
            const remainingTime = this.getRemainingLockoutTime();
            throw new Error(`Account locked. Try again in ${Math.ceil(remainingTime / 60000)} minutes.`);
        }

        // Validate input
        if (!username || !password) {
            throw new Error('Username and password are required');
        }

        try {
            const result = await api.login(username.trim(), password);
            
            // Reset login attempts on success
            this.resetLoginAttempts();
            
            // Set user data
            this.user = result.user;
            
            // Save login time
            setLocalStorage('last_login', new Date().toISOString());
            
            // Notify listeners
            this.notifyListeners();
            
            // Set up token refresh
            this.setupTokenRefresh();
            
            console.log('Login successful:', this.user.username);
            return result;
            
        } catch (error) {
            // Increment login attempts
            this.incrementLoginAttempts();
            
            // Re-throw error for handling by UI
            throw error;
        }
    }

    /**
     * Perform user logout
     */
    async logout(reason = 'user_action') {
        try {
            // Call logout endpoint if available
            if (api.token) {
                await api.logout();
            }
        } catch (error) {
            console.log('Logout API call failed:', error.message);
        } finally {
            // Clear local state regardless of API call result
            this.clearAuthState();
            
            console.log('Logout completed, reason:', reason);
        }
    }

    /**
     * Clear authentication state
     */
    clearAuthState() {
        this.user = null;
        api.setToken(null);
        
        // Clear auth-related localStorage
        removeLocalStorage('auth_token');
        removeLocalStorage('refresh_token');
        removeLocalStorage('last_login');
        
        // Clear token refresh timer
        this.clearTokenRefresh();
        
        // Notify listeners
        this.notifyListeners();
    }

    /**
     * Register new user
     */
    async register(userData) {
        const { username, email, password, confirmPassword } = userData;
        
        // Validate input
        if (!username || !email || !password) {
            throw new Error('All fields are required');
        }
        
        if (password !== confirmPassword) {
            throw new Error('Passwords do not match');
        }
        
        if (!isValidEmail(email)) {
            throw new Error('Invalid email address');
        }
        
        if (password.length < 8) {
            throw new Error('Password must be at least 8 characters long');
        }
        
        try {
            const result = await api.register({
                username: username.trim(),
                email: email.trim(),
                password
            });
            
            console.log('Registration successful');
            return result;
            
        } catch (error) {
            console.error('Registration failed:', error);
            throw error;
        }
    }

    /**
     * Update user profile
     */
    async updateProfile(profileData) {
        if (!this.isAuthenticated()) {
            throw new Error('User not authenticated');
        }

        try {
            const updatedProfile = await api.updateProfile(profileData);
            this.user = { ...this.user, ...updatedProfile };
            this.notifyListeners();
            return updatedProfile;
        } catch (error) {
            console.error('Profile update failed:', error);
            throw error;
        }
    }

    /**
     * Change user password
     */
    async changePassword(currentPassword, newPassword, confirmPassword) {
        if (!this.isAuthenticated()) {
            throw new Error('User not authenticated');
        }

        if (newPassword !== confirmPassword) {
            throw new Error('New passwords do not match');
        }

        if (newPassword.length < 8) {
            throw new Error('Password must be at least 8 characters long');
        }

        try {
            await api.changePassword({
                current_password: currentPassword,
                new_password: newPassword
            });
            
            console.log('Password changed successfully');
            showToast('Password changed successfully', 'success');
            
        } catch (error) {
            console.error('Password change failed:', error);
            throw error;
        }
    }

    /**
     * Setup automatic token refresh
     */
    setupTokenRefresh() {
        this.clearTokenRefresh();
        
        // Refresh token 5 minutes before expiration
        const refreshInterval = 55 * 60 * 1000; // 55 minutes
        
        this.refreshTimer = setInterval(async () => {
            if (this.isAuthenticated()) {
                try {
                    await api.refreshAccessToken();
                    console.log('Token refreshed automatically');
                } catch (error) {
                    console.error('Auto token refresh failed:', error);
                    this.logout('token_refresh_failed');
                }
            }
        }, refreshInterval);
    }

    /**
     * Clear token refresh timer
     */
    clearTokenRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }

    /**
     * Setup storage listener for multi-tab synchronization
     */
    setupStorageListener() {
        window.addEventListener('storage', (e) => {
            if (e.key === 'auth_token') {
                if (e.newValue === null) {
                    // Token was removed in another tab - logout
                    this.clearAuthState();
                } else if (e.oldValue === null) {
                    // Token was added in another tab - check auth
                    this.checkAuth();
                }
            }
        });
    }

    /**
     * Login attempt management
     */
    incrementLoginAttempts() {
        this.loginAttempts++;
        const attempts = getLocalStorage('login_attempts', 0) + 1;
        setLocalStorage('login_attempts', attempts);
        setLocalStorage('last_attempt', new Date().toISOString());
    }

    resetLoginAttempts() {
        this.loginAttempts = 0;
        removeLocalStorage('login_attempts');
        removeLocalStorage('last_attempt');
        removeLocalStorage('lockout_until');
    }

    isAccountLocked() {
        const attempts = getLocalStorage('login_attempts', 0);
        const lastAttempt = getLocalStorage('last_attempt');
        const lockoutUntil = getLocalStorage('lockout_until');

        if (attempts >= this.maxLoginAttempts) {
            if (!lockoutUntil) {
                // Set lockout time
                const lockoutTime = new Date(Date.now() + this.lockoutTime);
                setLocalStorage('lockout_until', lockoutTime.toISOString());
                return true;
            }

            const now = new Date();
            const lockout = new Date(lockoutUntil);
            
            if (now < lockout) {
                return true;
            } else {
                // Lockout expired, reset attempts
                this.resetLoginAttempts();
                return false;
            }
        }

        return false;
    }

    getRemainingLockoutTime() {
        const lockoutUntil = getLocalStorage('lockout_until');
        if (!lockoutUntil) return 0;

        const now = new Date();
        const lockout = new Date(lockoutUntil);
        return Math.max(0, lockout - now);
    }

    /**
     * Session management
     */
    getLastLoginTime() {
        const lastLogin = getLocalStorage('last_login');
        return lastLogin ? new Date(lastLogin) : null;
    }

    getSessionDuration() {
        const lastLogin = this.getLastLoginTime();
        if (!lastLogin) return 0;
        return Date.now() - lastLogin.getTime();
    }

    /**
     * Security helpers
     */
    isPasswordStrong(password) {
        const minLength = password.length >= 8;
        const hasUpperCase = /[A-Z]/.test(password);
        const hasLowerCase = /[a-z]/.test(password);
        const hasNumbers = /\d/.test(password);
        const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

        return {
            isValid: minLength && hasUpperCase && hasLowerCase && hasNumbers,
            strength: [minLength, hasUpperCase, hasLowerCase, hasNumbers, hasSpecialChar].filter(Boolean).length,
            requirements: {
                minLength,
                hasUpperCase,
                hasLowerCase,
                hasNumbers,
                hasSpecialChar
            }
        };
    }

    /**
     * Debug methods
     */
    getAuthState() {
        return {
            isAuthenticated: this.isAuthenticated(),
            user: this.user,
            hasToken: !!api.token,
            sessionDuration: this.getSessionDuration(),
            lastLogin: this.getLastLoginTime(),
            loginAttempts: getLocalStorage('login_attempts', 0),
            isLocked: this.isAccountLocked()
        };
    }

    /**
     * Cleanup on page unload
     */
    cleanup() {
        this.clearTokenRefresh();
        this.listeners = [];
    }
}

// Create global auth manager instance
const auth = new AuthManager();

// Initialize auth manager when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => auth.init());
} else {
    auth.init();
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => auth.cleanup());

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AuthManager, auth };
}

console.log('Auth manager loaded');