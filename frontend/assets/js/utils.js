// assets/js/utils.js - Utility Functions

/**
 * DOM Selection Utilities
 */
function $(selector) {
    return document.querySelector(selector);
}

function $$(selector) {
    return document.querySelectorAll(selector);
}

/**
 * DOM Manipulation Utilities
 */
function createElement(tag, className = '', innerHTML = '') {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (innerHTML) element.innerHTML = innerHTML;
    return element;
}

function showElement(element) {
    if (typeof element === 'string') element = $(element);
    if (element) element.classList.remove('hidden');
}

function hideElement(element) {
    if (typeof element === 'string') element = $(element);
    if (element) element.classList.add('hidden');
}

function toggleElement(element) {
    if (typeof element === 'string') element = $(element);
    if (element) element.classList.toggle('hidden');
}

function addClass(element, className) {
    if (typeof element === 'string') element = $(element);
    if (element) element.classList.add(className);
}

function removeClass(element, className) {
    if (typeof element === 'string') element = $(element);
    if (element) element.classList.remove(className);
}

function hasClass(element, className) {
    if (typeof element === 'string') element = $(element);
    return element ? element.classList.contains(className) : false;
}

/**
 * Date and Time Utilities
 */
function formatDate(date) {
    if (!date) return 'N/A';
    const d = new Date(date);
    return d.toLocaleDateString();
}

function formatDateTime(date) {
    if (!date) return 'N/A';
    const d = new Date(date);
    return d.toLocaleString();
}

function formatTime(date) {
    if (!date) return 'N/A';
    const d = new Date(date);
    return d.toLocaleTimeString();
}

function formatRelativeTime(date) {
    if (!date) return 'N/A';
    const now = new Date();
    const diffMs = now - new Date(date);
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    return formatDate(date);
}

/**
 * Performance Utilities
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Toast Notification System
 */
function showToast(message, type = 'info', duration = 3232) {
    // Remove existing toasts
    const existingToasts = $$('.toast');
    existingToasts.forEach(toast => toast.remove());

    const toast = createElement('div', `toast toast-${type}`, message);
    toast.style.position = 'fixed';
    toast.style.top = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '9999';
    toast.style.transform = 'translateX(400px)';
    toast.style.transition = 'transform 0.3s ease';

    document.body.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
    }, 100);
    
    // Auto remove
    setTimeout(() => {
        toast.style.transform = 'translateX(400px)';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 300);
    }, duration);

    // Click to dismiss
    toast.addEventListener('click', () => {
        toast.style.transform = 'translateX(400px)';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 300);
    });
}

/**
 * Modal Management
 */
function showModal(modalId) {
    const modal = $(modalId);
    if (modal) {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
        
        // Focus trap
        const focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        if (focusableElements.length > 0) {
            focusableElements[0].focus();
        }
    }
}

function hideModal(modalId) {
    const modal = $(modalId);
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
    }
}

function hideAllModals() {
    $$('.modal.show').forEach(modal => {
        modal.classList.remove('show');
    });
    document.body.style.overflow = '';
}

/**
 * Loading States
 */
function showLoading(element) {
    if (typeof element === 'string') element = $(element);
    if (element) {
        element.classList.add('loading');
        element.disabled = true;
    }
}

function hideLoading(element) {
    if (typeof element === 'string') element = $(element);
    if (element) {
        element.classList.remove('loading');
        element.disabled = false;
    }
}

/**
 * Device and Status Utilities
 */
function getDeviceIcon(type) {
    const icons = {
        router: 'fas fa-network-wired',
        switch: 'fas fa-project-diagram',
        server: 'fas fa-server',
        wireless: 'fas fa-wifi',
        firewall: 'fas fa-shield-alt',
        laptop: 'fas fa-laptop',
        desktop: 'fas fa-desktop',
        printer: 'fas fa-print',
        phone: 'fas fa-phone',
        camera: 'fas fa-video'
    };
    return icons[type] || 'fas fa-question-circle';
}

function getStatusBadge(status) {
    const classes = {
        active: 'badge-success',
        inactive: 'badge-danger',
        warning: 'badge-warning',
        pending: 'badge-warning',
        completed: 'badge-success',
        failed: 'badge-danger',
        running: 'badge-info',
        paused: 'badge-secondary',
        up: 'badge-success',
        down: 'badge-danger',
        unknown: 'badge-secondary'
    };
    const className = classes[status?.toLowerCase()] || 'badge-secondary';
    return `<span class="badge ${className}">${status}</span>`;
}

function getDeviceTypeColor(type) {
    const colors = {
        router: '#3b82f6',
        switch: '#10b981',
        server: '#f59e0b',
        wireless: '#8b5cf6',
        firewall: '#ef4444'
    };
    return colors[type] || '#64748b';
}

/**
 * Data Formatting Utilities
 */
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function formatPercentage(value, decimals = 1) {
    if (value === null || value === undefined) return 'N/A';
    return `${parseFloat(value).toFixed(decimals)}%`;
}

function formatNumber(value, decimals = 0) {
    if (value === null || value === undefined) return 'N/A';
    return parseFloat(value).toFixed(decimals);
}

function formatCurrency(value, currency = 'USD') {
    if (value === null || value === undefined) return 'N/A';
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(value);
}

/**
 * File and Download Utilities
 */
function downloadFile(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

function downloadJSON(data, filename) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { 
        type: 'application/json' 
    });
    downloadFile(blob, filename);
}

function downloadCSV(data, filename) {
    if (!Array.isArray(data) || data.length === 0) {
        showToast('No data to export', 'warning');
        return;
    }
    
    const headers = Object.keys(data[0]);
    const csvContent = [
        headers.join(','),
        ...data.map(row => headers.map(header => 
            JSON.stringify(row[header] || '')
        ).join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    downloadFile(blob, filename);
}

/**
 * Clipboard Utilities
 */
function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(() => {
            showToast('Copied to clipboard', 'success');
        }).catch(() => {
            showToast('Failed to copy to clipboard', 'error');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'absolute';
        textArea.style.left = '-999999px';
        document.body.prepend(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            showToast('Copied to clipboard', 'success');
        } catch (error) {
            showToast('Failed to copy to clipboard', 'error');
        } finally {
            textArea.remove();
        }
    }
}

/**
 * URL and Query Parameter Utilities
 */
function getQueryParams() {
    const params = new URLSearchParams(window.location.search);
    const result = {};
    for (const [key, value] of params) {
        result[key] = value;
    }
    return result;
}

function setQueryParam(key, value) {
    const url = new URL(window.location);
    url.searchParams.set(key, value);
    window.history.pushState({}, '', url);
}

function removeQueryParam(key) {
    const url = new URL(window.location);
    url.searchParams.delete(key);
    window.history.pushState({}, '', url);
}

/**
 * Storage Utilities
 */
function setLocalStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
        return true;
    } catch (error) {
        console.error('Failed to save to localStorage:', error);
        return false;
    }
}

function getLocalStorage(key, defaultValue = null) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
        console.error('Failed to read from localStorage:', error);
        return defaultValue;
    }
}

function removeLocalStorage(key) {
    try {
        localStorage.removeItem(key);
        return true;
    } catch (error) {
        console.error('Failed to remove from localStorage:', error);
        return false;
    }
}

function clearLocalStorage() {
    try {
        localStorage.clear();
        return true;
    } catch (error) {
        console.error('Failed to clear localStorage:', error);
        return false;
    }
}

/**
 * Validation Utilities
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidIP(ip) {
    const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    return ipRegex.test(ip);
}

function isValidPort(port) {
    const portNum = parseInt(port);
    return !isNaN(portNum) && portNum >= 1 && portNum <= 65535;
}

function isValidURL(url) {
    try {
        new URL(url);
        return true;
    } catch {
        return false;
    }
}

/**
 * Math Utilities
 */
function randomBetween(min, max) {
    return Math.random() * (max - min) + min;
}

function randomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
}

function lerp(start, end, progress) {
    return start + (end - start) * progress;
}

/**
 * Array Utilities
 */
function uniqueArray(array) {
    return [...new Set(array)];
}

function shuffleArray(array) {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
}

function groupBy(array, key) {
    return array.reduce((groups, item) => {
        const group = item[key];
        groups[group] = groups[group] || [];
        groups[group].push(item);
        return groups;
    }, {});
}

function sortBy(array, key, direction = 'asc') {
    return [...array].sort((a, b) => {
        const aVal = a[key];
        const bVal = b[key];
        
        if (aVal < bVal) return direction === 'asc' ? -1 : 1;
        if (aVal > bVal) return direction === 'asc' ? 1 : -1;
        return 0;
    });
}

/**
 * Object Utilities
 */
function deepClone(obj) {
    return JSON.parse(JSON.stringify(obj));
}

function mergeObjects(...objects) {
    return Object.assign({}, ...objects);
}

function objectToQueryString(obj) {
    const params = new URLSearchParams();
    for (const [key, value] of Object.entries(obj)) {
        if (value !== null && value !== undefined) {
            params.append(key, value);
        }
    }
    return params.toString();
}

/**
 * Error Handling Utilities
 */
function handleError(error, context = '') {
    console.error(`Error in ${context}:`, error);
    
    let message = 'An unexpected error occurred';
    if (error.message) {
        message = error.message;
    } else if (typeof error === 'string') {
        message = error;
    }
    
    showToast(message, 'error');
}

function safeExecute(fn, fallback = null) {
    try {
        return fn();
    } catch (error) {
        console.error('Safe execute failed:', error);
        return fallback;
    }
}

/**
 * Animation Utilities
 */
function animateValue(start, end, duration, callback) {
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        const current = start + (end - start) * easeOutQuart;
        
        callback(current);
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

function fadeIn(element, duration = 300) {
    element.style.opacity = 0;
    element.style.transition = `opacity ${duration}ms ease`;
    showElement(element);
    
    setTimeout(() => {
        element.style.opacity = 1;
    }, 10);
}

function fadeOut(element, duration = 300) {
    element.style.opacity = 1;
    element.style.transition = `opacity ${duration}ms ease`;
    
    setTimeout(() => {
        element.style.opacity = 0;
        setTimeout(() => {
            hideElement(element);
        }, duration);
    }, 10);
}

/**
 * Global Event Utilities
 */
function onEscape(callback) {
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            callback(e);
        }
    });
}

function onEnter(element, callback) {
    element.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            callback(e);
        }
    });
}

function onClickOutside(element, callback) {
    document.addEventListener('click', (e) => {
        if (!element.contains(e.target)) {
            callback(e);
        }
    });
}

/**
 * Initialize utility functions
 */
function initializeUtils() {
    // Global keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Escape key - close modals
        if (e.key === 'Escape') {
            hideAllModals();
        }
    });
    
    // Global click handler for modal close buttons
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal-close')) {
            const modal = e.target.closest('.modal');
            if (modal) {
                hideModal('#' + modal.id);
            }
        }
    });
    
    console.log('Utils initialized');
}

// Auto-initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeUtils);
} else {
    initializeUtils();
}