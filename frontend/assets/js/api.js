// // frontend/assets/js/api.js
// class APIClient {
//     constructor(baseURL = 'http://localhost:5000/api') {
//         this.baseURL = baseURL;
//         this.token = localStorage.getItem('auth_token');
//     }

//     setToken(token) {
//         this.token = token;
//         if (token) {
//             localStorage.setItem('auth_token', token);
//         } else {
//             localStorage.removeItem('auth_token');
//         }
//     }

//     async request(endpoint, options = {}) {
//         const url = `${this.baseURL}${endpoint}`;
//         const config = {
//             headers: {
//                 'Content-Type': 'application/json',
//                 ...options.headers
//             },
//             ...options
//         };

//         if (this.token) {
//             config.headers.Authorization = `Bearer ${this.token}`;
//         }

//         try {
//             const response = await fetch(url, config);
            
//             if (!response.ok) {
//                 const error = await response.json().catch(() => ({ message: 'Network error' }));
//                 throw new Error(error.message || `HTTP ${response.status}`);
//             }

//             return await response.json();
//         } catch (error) {
//             console.error('API Request failed:', error);
//             throw error;
//         }
//     }

//     // Authentication
//     async login(username, password) {
//         const response = await this.request('/auth/login', {
//             method: 'POST',
//             body: JSON.stringify({ username, password })
//         });
//         this.setToken(response.access_token);
//         return response;
//     }

//     async logout() {
//         this.setToken(null);
//     }

//     async getProfile() {
//         return this.request('/auth/profile');
//     }

//     // Devices
//     async getDevices() {
//         return this.request('/devices');
//     }

//     async getDevice(id) {
//         return this.request(`/devices/${id}`);
//     }

//     async createDevice(device) {
//         return this.request('/devices', {
//             method: 'POST',
//             body: JSON.stringify(device)
//         });
//     }

//     async updateDevice(id, device) {
//         return this.request(`/devices/${id}`, {
//             method: 'PUT',
//             body: JSON.stringify(device)
//         });
//     }

//     async deleteDevice(id) {
//         return this.request(`/devices/${id}`, {
//             method: 'DELETE'
//         });
//     }

//     // Inventory
//     async getInventory() {
//         return this.request('/inventory');
//     }

//     async getDeviceInventory(deviceId) {
//         return this.request(`/inventory/${deviceId}`);
//     }

//     async scanDeviceInventory(deviceId) {
//         return this.request(`/inventory/scan/${deviceId}`, {
//             method: 'POST'
//         });
//     }

//     // Provisioning
//     async getTemplates() {
//         return this.request('/provisioning/templates');
//     }

//     async createTemplate(template) {
//         return this.request('/provisioning/templates', {
//             method: 'POST',
//             body: JSON.stringify(template)
//         });
//     }

//     async getProvisioningTasks() {
//         return this.request('/provisioning/tasks');
//     }

//     async createProvisioningTask(task) {
//         return this.request('/provisioning/tasks', {
//             method: 'POST',
//             body: JSON.stringify(task)
//         });
//     }

//     // Telemetry
//     async getTelemetryData(deviceId, params = {}) {
//         const query = new URLSearchParams(params).toString();
//         return this.request(`/telemetry/data/${deviceId}?${query}`);
//     }

//     async configureTelemetry(deviceId, config) {
//         return this.request(`/telemetry/config/${deviceId}`, {
//             method: 'POST',
//             body: JSON.stringify(config)
//         });
//     }

//     async collectTelemetry(deviceId) {
//         return this.request(`/telemetry/collect/${deviceId}`, {
//             method: 'POST'
//         });
//     }

//     // Reports
//     async getReports() {
//         return this.request('/reports');
//     }

//     async createReport(report) {
//         return this.request('/reports', {
//             method: 'POST',
//             body: JSON.stringify(report)
//         });
//     }

//     async downloadReport(reportId) {
//         const response = await fetch(`${this.baseURL}/reports/download/${reportId}`, {
//             headers: {
//                 Authorization: `Bearer ${this.token}`
//             }
//         });
//         return response.blob();
//     }

//     // Topology
//     async getTopology() {
//         return this.request('/topology');
//     }

//     async saveTopology(topology) {
//         return this.request('/topology', {
//             method: 'POST',
//             body: JSON.stringify(topology)
//         });
//     }
// }

// // Global API instance
// const api = new APIClient();

// // frontend/assets/js/auth.js
// class AuthManager {
//     constructor() {
//         this.user = null;
//         this.listeners = [];
//     }

//     addListener(callback) {
//         this.listeners.push(callback);
//     }

//     removeListener(callback) {
//         this.listeners = this.listeners.filter(l => l !== callback);
//     }

//     notifyListeners() {
//         this.listeners.forEach(callback => callback(this.user));
//     }

//     async login(username, password) {
//         try {
//             const result = await api.login(username, password);
//             this.user = result.user;
//             this.notifyListeners();
//             return result;
//         } catch (error) {
//             throw error;
//         }
//     }

//     async logout() {
//         await api.logout();
//         this.user = null;
//         this.notifyListeners();
//     }

//     async checkAuth() {
//         try {
//             const profile = await api.getProfile();
//             this.user = profile;
//             this.notifyListeners();
//             return true;
//         } catch (error) {
//             this.user = null;
//             this.notifyListeners();
//             return false;
//         }
//     }

//     isAuthenticated() {
//         return !!this.user;
//     }

//     getUser() {
//         return this.user;
//     }
// }

// // Global auth manager
// const auth = new AuthManager();

// // frontend/assets/js/utils.js
// // Utility functions for common operations

// function $(selector) {
//     return document.querySelector(selector);
// }

// function $$(selector) {
//     return document.querySelectorAll(selector);
// }

// function createElement(tag, className = '', innerHTML = '') {
//     const element = document.createElement(tag);
//     if (className) element.className = className;
//     if (innerHTML) element.innerHTML = innerHTML;
//     return element;
// }

// function showElement(element) {
//     if (typeof element === 'string') element = $(element);
//     element?.classList.remove('hidden');
// }

// function hideElement(element) {
//     if (typeof element === 'string') element = $(element);
//     element?.classList.add('hidden');
// }

// function toggleElement(element) {
//     if (typeof element === 'string') element = $(element);
//     element?.classList.toggle('hidden');
// }

// function formatDate(date) {
//     return new Date(date).toLocaleDateString();
// }

// function formatDateTime(date) {
//     return new Date(date).toLocaleString();
// }

// function debounce(func, wait) {
//     let timeout;
//     return function executedFunction(...args) {
//         const later = () => {
//             clearTimeout(timeout);
//             func(...args);
//         };
//         clearTimeout(timeout);
//         timeout = setTimeout(later, wait);
//     };
// }

// function throttle(func, limit) {
//     let inThrottle;
//     return function() {
//         const args = arguments;
//         const context = this;
//         if (!inThrottle) {
//             func.apply(context, args);
//             inThrottle = true;
//             setTimeout(() => inThrottle = false, limit);
//         }
//     };
// }

// function showToast(message, type = 'info') {
//     const toast = createElement('div', `toast toast-${type}`, message);
//     document.body.appendChild(toast);
    
//     setTimeout(() => toast.classList.add('show'), 100);
//     setTimeout(() => {
//         toast.classList.remove('show');
//         setTimeout(() => toast.remove(), 300);
//     }, 3232);
// }

// function showModal(modalId) {
//     const modal = $(modalId);
//     if (modal) {
//         modal.classList.add('show');
//         document.body.style.overflow = 'hidden';
//     }
// }

// function hideModal(modalId) {
//     const modal = $(modalId);
//     if (modal) {
//         modal.classList.remove('show');
//         document.body.style.overflow = '';
//     }
// }

// function getDeviceIcon(type) {
//     const icons = {
//         router: 'fas fa-network-wired',
//         switch: 'fas fa-project-diagram',
//         server: 'fas fa-server',
//         wireless: 'fas fa-wifi',
//         firewall: 'fas fa-shield-alt'
//     };
//     return icons[type] || 'fas fa-desktop';
// }

// function getStatusBadge(status) {
//     const classes = {
//         active: 'badge-success',
//         inactive: 'badge-danger',
//         warning: 'badge-warning',
//         pending: 'badge-warning',
//         completed: 'badge-success',
//         failed: 'badge-danger'
//     };
//     return `<span class="badge ${classes[status] || 'badge-secondary'}">${status}</span>`;
// }

// function copyToClipboard(text) {
//     navigator.clipboard.writeText(text).then(() => {
//         showToast('Copied to clipboard', 'success');
//     }).catch(() => {
//         showToast('Failed to copy to clipboard', 'error');
//     });
// }

// function downloadFile(blob, filename) {
//     const url = window.URL.createObjectURL(blob);
//     const a = document.createElement('a');
//     a.href = url;
//     a.download = filename;
//     document.body.appendChild(a);
//     a.click();
//     window.URL.revokeObjectURL(url);
//     document.body.removeChild(a);
// }

// // frontend/assets/js/dashboard.js
// class Dashboard {
//     constructor() {
//         this.refreshInterval = null;
//         this.charts = {};
//     }

//     async init() {
//         await this.loadStats();
//         await this.loadRecentDevices();
//         await this.loadSystemHealth();
//         this.startAutoRefresh();
//     }

//     async loadStats() {
//         try {
//             const devices = await api.getDevices();
//             const totalDevices = devices.length;
//             const activeDevices = devices.filter(d => d.status === 'active').length;
//             const inactiveDevices = totalDevices - activeDevices;

//             $('#totalDevices').textContent = totalDevices;
//             $('#activeDevices').textContent = activeDevices;
//             $('#inactiveDevices').textContent = inactiveDevices;

//             // You could also get reports count from API
//             // const reports = await api.getReports();
//             // $('#totalReports').textContent = reports.length;
//         } catch (error) {
//             console.error('Failed to load stats:', error);
//         }
//     }

//     async loadRecentDevices() {
//         try {
//             const devices = await api.getDevices();
//             const tbody = $('#recentDevicesTable');
//             tbody.innerHTML = '';

//             devices.slice(0, 5).forEach(device => {
//                 const row = createElement('tr');
//                 row.innerHTML = `
//                     <td>
//                         <div class="flex items-center">
//                             <i class="${getDeviceIcon(device.device_type)}" style="margin-right: 8px; color: var(--primary-color);"></i>
//                             ${device.name}
//                         </div>
//                     </td>
//                     <td style="text-transform: capitalize;">${device.device_type}</td>
//                     <td>${getStatusBadge(device.status)}</td>
//                 `;
//                 tbody.appendChild(row);
//             });
//         } catch (error) {
//             console.error('Failed to load recent devices:', error);
//         }
//     }

//     async loadSystemHealth() {
//         // Simulate system health metrics
//         // In a real application, this would come from monitoring APIs
//         const healthData = [
//             { name: 'CPU Usage', value: Math.random() * 100, unit: '%' },
//             { name: 'Memory Usage', value: Math.random() * 100, unit: '%' },
//             { name: 'Disk Usage', value: Math.random() * 100, unit: '%' },
//             { name: 'Network Traffic', value: 'Normal', unit: '' }
//         ];

//         const healthContainer = $('#systemHealth');
//         if (healthContainer) {
//             healthContainer.innerHTML = healthData.map(metric => {
//                 let badgeClass = 'badge-success';
//                 if (typeof metric.value === 'number') {
//                     if (metric.value > 80) badgeClass = 'badge-danger';
//                     else if (metric.value > 60) badgeClass = 'badge-warning';
//                 }

//                 const displayValue = typeof metric.value === 'number' 
//                     ? `${Math.round(metric.value)}${metric.unit}`
//                     : metric.value;

//                 return `
//                     <div class="flex items-center justify-between">
//                         <span>${metric.name}</span>
//                         <span class="badge ${badgeClass}">${displayValue}</span>
//                     </div>
//                 `;
//             }).join('');
//         }
//     }

//     startAutoRefresh() {
//         this.refreshInterval = setInterval(() => {
//             this.loadStats();
//             this.loadSystemHealth();
//         }, 32320); // Refresh every 30 seconds
//     }

//     stopAutoRefresh() {
//         if (this.refreshInterval) {
//             clearInterval(this.refreshInterval);
//             this.refreshInterval = null;
//         }
//     }

//     destroy() {
//         this.stopAutoRefresh();
//     }
// }

// // frontend/assets/js/devices.js
// class DeviceManager {
//     constructor() {
//         this.devices = [];
//         this.selectedDevice = null;
//     }

//     async init() {
//         this.setupEventListeners();
//         await this.loadDevices();
//     }

//     setupEventListeners() {
//         $('#addDeviceBtn')?.addEventListener('click', () => this.showAddDeviceModal());
//         $('#saveDeviceBtn')?.addEventListener('click', () => this.saveDevice());
        
//         // Modal close handlers
//         $$('.modal-close').forEach(btn => {
//             btn.addEventListener('click', (e) => {
//                 const modal = e.target.closest('.modal');
//                 if (modal) hideElement(modal);
//             });
//         });
//     }

//     async loadDevices() {
//         try {
//             this.devices = await api.getDevices();
//             this.renderDevicesTable();
//         } catch (error) {
//             console.error('Failed to load devices:', error);
//             showToast('Failed to load devices', 'error');
//         }
//     }

//     renderDevicesTable() {
//         const tbody = $('#devicesTable');
//         if (!tbody) return;

//         tbody.innerHTML = '';

//         this.devices.forEach(device => {
//             const row = createElement('tr');
//             row.innerHTML = `
//                 <td>
//                     <div class="flex items-center">
//                         <i class="${getDeviceIcon(device.device_type)}" style="margin-right: 8px; color: var(--primary-color);"></i>
//                         ${device.name}
//                     </div>
//                 </td>
//                 <td style="text-transform: capitalize;">${device.device_type}</td>
//                 <td>${device.ip_address}</td>
//                 <td>${getStatusBadge(device.status)}</td>
//                 <td>
//                     <div class="flex gap-2">
//                         <button class="btn btn-outline" style="padding: 6px 8px;" onclick="deviceManager.editDevice(${device.id})">
//                             <i class="fas fa-edit"></i>
//                         </button>
//                         <button class="btn btn-outline" style="padding: 6px 8px;" onclick="deviceManager.viewDevice(${device.id})">
//                             <i class="fas fa-eye"></i>
//                         </button>
//                         <button class="btn btn-danger" style="padding: 6px 8px;" onclick="deviceManager.deleteDevice(${device.id})">
//                             <i class="fas fa-trash"></i>
//                         </button>
//                     </div>
//                 </td>
//             `;
//             tbody.appendChild(row);
//         });
//     }

//     showAddDeviceModal() {
//         // Clear form
//         $('#deviceName').value = '';
//         $('#deviceType').value = 'router';
//         $('#deviceIP').value = '';
//         $('#deviceUsername').value = '';
//         $('#devicePassword').value = '';
        
//         showModal('#addDeviceModal');
//     }

//     async saveDevice() {
//         const device = {
//             name: $('#deviceName').value.trim(),
//             device_type: $('#deviceType').value,
//             ip_address: $('#deviceIP').value.trim(),
//             username: $('#deviceUsername').value.trim(),
//             password: $('#devicePassword').value
//         };

//         if (!device.name || !device.ip_address) {
//             showToast('Please fill in required fields', 'error');
//             return;
//         }

//         try {
//             await api.createDevice(device);
//             hideModal('#addDeviceModal');
//             await this.loadDevices();
//             showToast('Device added successfully', 'success');
//         } catch (error) {
//             console.error('Failed to add device:', error);
//             showToast('Failed to add device: ' + error.message, 'error');
//         }
//     }

//     async editDevice(id) {
//         const device = this.devices.find(d => d.id === id);
//         if (!device) return;

//         // Populate form with device data
//         $('#deviceName').value = device.name;
//         $('#deviceType').value = device.device_type;
//         $('#deviceIP').value = device.ip_address;
//         $('#deviceUsername').value = device.username || '';
        
//         this.selectedDevice = device;
//         showModal('#addDeviceModal');
        
//         // Change button text to "Update"
//         $('#saveDeviceBtn').textContent = 'Update Device';
//     }

//     async viewDevice(id) {
//         const device = this.devices.find(d => d.id === id);
//         if (!device) return;

//         try {
//             const detailedDevice = await api.getDevice(id);
//             // Show device details modal or navigate to device detail page
//             alert(`Device Details:\n\nName: ${detailedDevice.name}\nType: ${detailedDevice.device_type}\nIP: ${detailedDevice.ip_address}\nStatus: ${detailedDevice.status}`);
//         } catch (error) {
//             console.error('Failed to get device details:', error);
//             showToast('Failed to load device details', 'error');
//         }
//     }

//     async deleteDevice(id) {
//         if (!confirm('Are you sure you want to delete this device?')) return;

//         try {
//             await api.deleteDevice(id);
//             await this.loadDevices();
//             showToast('Device deleted successfully', 'success');
//         } catch (error) {
//             console.error('Failed to delete device:', error);
//             showToast('Failed to delete device: ' + error.message, 'error');
//         }
//     }
// }

// // Global device manager instance
// const deviceManager = new DeviceManager();

// // frontend/assets/js/topology.js
// class TopologyBuilder {
//     constructor() {
//         this.devices = [];
//         this.connections = [];
//         this.selectedDevice = null;
//         this.currentTool = 'select';
//         this.connectionStart = null;
//         this.deviceCounter = 1;
//         this.canvas = null;
//         this.isDragging = false;
//         this.draggedDeviceType = null;
//     }

//     async init() {
//         this.canvas = $('#topologyCanvas');
//         if (!this.canvas) return;

//         this.setupEventListeners();
//         this.setupDragAndDrop();
//         await this.loadTopology();
//         this.render();
//     }

//     setupEventListeners() {
//         // Tool buttons
//         $('#selectTool')?.addEventListener('click', () => this.setTool('select'));
//         $('#connectTool')?.addEventListener('click', () => this.setTool('connect'));
//         $('#clearCanvas')?.addEventListener('click', () => this.clearCanvas());

//         // Canvas click
//         this.canvas?.addEventListener('click', (e) => this.handleCanvasClick(e));

//         // Save topology button (if exists)
//         $('#saveTopology')?.addEventListener('click', () => this.saveTopology());
//     }

//     setupDragAndDrop() {
//         // Handle device palette drag start
//         $$('.device-item').forEach(item => {
//             item.addEventListener('dragstart', (e) => {
//                 this.draggedDeviceType = e.target.closest('.device-item').getAttribute('data-device-type');
//                 e.dataTransfer.effectAllowed = 'copy';
//             });
//         });

//         // Handle canvas drop
//         this.canvas?.addEventListener('dragover', (e) => {
//             e.preventDefault();
//             e.dataTransfer.dropEffect = 'copy';
//             this.canvas.classList.add('drag-over');
//         });

//         this.canvas?.addEventListener('dragleave', () => {
//             this.canvas.classList.remove('drag-over');
//         });

//         this.canvas?.addEventListener('drop', (e) => {
//             e.preventDefault();
//             this.canvas.classList.remove('drag-over');
//             this.handleDrop(e);
//         });
//     }

//     handleDrop(e) {
//         if (!this.draggedDeviceType) return;

//         const rect = this.canvas.getBoundingClientRect();
//         const x = e.clientX - rect.left - 40; // Center the device
//         const y = e.clientY - rect.top - 40;

//         const device = {
//             id: Date.now(),
//             name: `${this.draggedDeviceType.charAt(0).toUpperCase() + this.draggedDeviceType.slice(1)}-${this.deviceCounter++}`,
//             type: this.draggedDeviceType,
//             x: Math.max(0, Math.min(x, rect.width - 80)),
//             y: Math.max(0, Math.min(y, rect.height - 80)),
//             ports: this.generatePortsForDevice(this.draggedDeviceType)
//         };

//         this.devices.push(device);
//         this.render();
//         this.updateCanvasStatus('Device added! Click to select or use tools to connect');

//         this.draggedDeviceType = null;
//     }

//     generatePortsForDevice(type) {
//         const portCounts = {
//             router: 4,
//             switch: 24,
//             server: 2,
//             wireless: 1,
//             firewall: 4
//         };

//         const count = portCounts[type] || 4;
//         const ports = [];

//         for (let i = 0; i < count; i++) {
//             ports.push({
//                 id: `${Date.now()}-${i}`,
//                 name: `Port ${i + 1}`,
//                 type: type === 'server' ? 'ethernet' : 'gigabit',
//                 connected: false
//             });
//         }

//         return ports;
//     }

//     handleCanvasClick(e) {
//         if (e.target !== this.canvas) return;

//         // Deselect all devices
//         this.selectedDevice = null;
//         this.updatePropertiesPanel();
//         this.render();
//     }

//     setTool(tool) {
//         this.currentTool = tool;
//         this.connectionStart = null;

//         // Update tool buttons
//         $$('.tool-btn').forEach(btn => btn.classList.remove('active'));
//         $(`#${tool}Tool`)?.classList.add('active');

//         // Update canvas cursor and status
//         const statusMessages = {
//             select: 'Click devices to select them',
//             connect: 'Click devices to connect them'
//         };

//         this.canvas.style.cursor = tool === 'connect' ? 'crosshair' : 'default';
//         this.updateCanvasStatus(statusMessages[tool] || 'Tool selected');
//     }

//     handleDeviceClick(device, e) {
//         e.stopPropagation();

//         if (this.currentTool === 'select') {
//             this.selectDevice(device);
//         } else if (this.currentTool === 'connect') {
//             this.handleConnectionTool(device);
//         }
//     }

//     selectDevice(device) {
//         this.selectedDevice = device;
//         this.updatePropertiesPanel();
//         this.render();
//     }

//     handleConnectionTool(device) {
//         if (!this.connectionStart) {
//             this.connectionStart = device;
//             this.updateCanvasStatus(`Click another device to connect to ${device.name}`);
//         } else if (this.connectionStart.id !== device.id) {
//             this.createConnection(this.connectionStart, device);
//             this.connectionStart = null;
//             this.updateCanvasStatus('Connection created! Click devices to connect them');
//         }
//     }

//     createConnection(device1, device2) {
//         // Check if connection already exists
//         const exists = this.connections.some(conn => 
//             (conn.from === device1.id && conn.to === device2.id) ||
//             (conn.from === device2.id && conn.to === device1.id)
//         );

//         if (exists) {
//             showToast('Connection already exists between these devices', 'warning');
//             return;
//         }

//         const connection = {
//             id: Date.now(),
//             from: device1.id,
//             to: device2.id,
//             fromPort: device1.ports[0]?.id,
//             toPort: device2.ports[0]?.id
//         };

//         this.connections.push(connection);
//         this.render();
//         showToast('Connection created successfully', 'success');
//     }

//     removeConnection(connectionId) {
//         this.connections = this.connections.filter(c => c.id !== connectionId);
//         this.render();
//     }

//     removeDevice(deviceId) {
//         if (!confirm('Remove this device and all its connections?')) return;

//         // Remove device
//         this.devices = this.devices.filter(d => d.id !== deviceId);

//         // Remove related connections
//         this.connections = this.connections.filter(c => 
//             c.from !== deviceId && c.to !== deviceId
//         );

//         // Clear selection if removed device was selected
//         if (this.selectedDevice?.id === deviceId) {
//             this.selectedDevice = null;
//             this.updatePropertiesPanel();
//         }

//         this.render();
//         showToast('Device removed successfully', 'success');
//     }

//     clearCanvas() {
//         if (!confirm('Clear the entire topology? This cannot be undone.')) return;

//         this.devices = [];
//         this.connections = [];
//         this.selectedDevice = null;
//         this.connectionStart = null;
//         this.deviceCounter = 1;

//         this.updatePropertiesPanel();
//         this.render();
//         this.updateCanvasStatus('Canvas cleared. Drag devices from the library to get started');
//     }

//     render() {
//         this.canvas.innerHTML = '';

//         // Render connections first (so they appear behind devices)
//         this.connections.forEach(connection => {
//             this.renderConnection(connection);
//         });

//         // Render devices
//         this.devices.forEach(device => {
//             this.renderDevice(device);
//         });
//     }

//     renderDevice(device) {
//         const deviceEl = createElement('div', 'network-device');
//         deviceEl.style.left = device.x + 'px';
//         deviceEl.style.top = device.y + 'px';
//         deviceEl.setAttribute('data-device-id', device.id);

//         if (this.selectedDevice?.id === device.id) {
//             deviceEl.classList.add('selected');
//         }

//         deviceEl.innerHTML = `
//             <div class="device-icon">
//                 <i class="${getDeviceIcon(device.type)}"></i>
//             </div>
//             <div class="device-label">${device.name}</div>
//         `;

//         // Add event listeners
//         deviceEl.addEventListener('click', (e) => this.handleDeviceClick(device, e));
//         this.makeDeviceDraggable(deviceEl, device);

//         this.canvas.appendChild(deviceEl);
//     }

//     makeDeviceDraggable(element, device) {
//         let isDragging = false;
//         let startX, startY;

//         element.addEventListener('mousedown', (e) => {
//             if (this.currentTool !== 'select') return;

//             isDragging = true;
//             startX = e.clientX - device.x;
//             startY = e.clientY - device.y;
//             element.style.zIndex = '1000';
//             e.preventDefault();
//         });

//         document.addEventListener('mousemove', (e) => {
//             if (!isDragging) return;

//             const rect = this.canvas.getBoundingClientRect();
//             device.x = Math.max(0, Math.min(e.clientX - startX, rect.width - 80));
//             device.y = Math.max(0, Math.min(e.clientY - startY, rect.height - 80));

//             element.style.left = device.x + 'px';
//             element.style.top = device.y + 'px';

//             // Update connections
//             this.render();
//         });

//         document.addEventListener('mouseup', () => {
//             if (isDragging) {
//                 isDragging = false;
//                 element.style.zIndex = '';
//             }
//         });
//     }

//     renderConnection(connection) {
//         const device1 = this.devices.find(d => d.id === connection.from);
//         const device2 = this.devices.find(d => d.id === connection.to);

//         if (!device1 || !device2) return;

//         const line = createElement('div', 'connection-line');
//         line.setAttribute('data-connection-id', connection.id);

//         this.updateConnectionPosition(line, device1, device2);

//         line.addEventListener('click', (e) => {
//             e.stopPropagation();
//             if (confirm('Remove this connection?')) {
//                 this.removeConnection(connection.id);
//             }
//         });

//         this.canvas.appendChild(line);
//     }

//     updateConnectionPosition(line, device1, device2) {
//         const x1 = device1.x + 40; // Center of device
//         const y1 = device1.y + 40;
//         const x2 = device2.x + 40;
//         const y2 = device2.y + 40;

//         const length = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
//         const angle = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI;

//         line.style.left = x1 + 'px';
//         line.style.top = y1 + 'px';
//         line.style.width = length + 'px';
//         line.style.transform = `rotate(${angle}deg)`;
//     }

//     updatePropertiesPanel() {
//         const panel = $('#deviceProperties');
//         if (!panel) return;

//         if (this.selectedDevice) {
//             panel.innerHTML = `
//                 <div class="form-group">
//                     <label class="form-label">Name</label>
//                     <input type="text" class="form-input" value="${this.selectedDevice.name}" 
//                            onchange="topologyBuilder.updateDeviceName(${this.selectedDevice.id}, this.value)">
//                 </div>
//                 <div class="form-group">
//                     <label class="form-label">Type</label>
//                     <div style="text-transform: capitalize;">${this.selectedDevice.type}</div>
//                 </div>
//                 <div class="form-group">
//                     <label class="form-label">Position</label>
//                     <div>X: ${Math.round(this.selectedDevice.x)}, Y: ${Math.round(this.selectedDevice.y)}</div>
//                 </div>
//                 <div class="form-group">
//                     <label class="form-label">Ports</label>
//                     <div style="font-size: 0.875rem; color: var(--text-secondary);">
//                         ${this.selectedDevice.ports?.length || 0} ports available
//                     </div>
//                 </div>
//                 <button class="btn btn-danger" style="width: 100%; margin-top: 12px;" 
//                         onclick="topologyBuilder.removeDevice(${this.selectedDevice.id})">
//                     <i class="fas fa-trash"></i>
//                     Remove Device
//                 </button>
//             `;
//         } else {
//             panel.innerHTML = '<p class="text-sm" style="color: var(--text-secondary);">Select a device to view properties</p>';
//         }
//     }

//     updateDeviceName(deviceId, newName) {
//         const device = this.devices.find(d => d.id === deviceId);
//         if (device && newName.trim()) {
//             device.name = newName.trim();
//             this.render();
//         }
//     }

//     updateCanvasStatus(message) {
//         const statusEl = $('#canvasStatus');
//         if (statusEl) {
//             statusEl.textContent = message;
//         }
//     }

//     async loadTopology() {
//         try {
//             // In a real application, load topology from API
//             // const topology = await api.getTopology();
//             // this.devices = topology.devices || [];
//             // this.connections = topology.connections || [];
//         } catch (error) {
//             console.error('Failed to load topology:', error);
//         }
//     }

//     async saveTopology() {
//         try {
//             const topology = {
//                 devices: this.devices,
//                 connections: this.connections
//             };

//             // In a real application, save to API
//             // await api.saveTopology(topology);
            
//             showToast('Topology saved successfully', 'success');
//         } catch (error) {
//             console.error('Failed to save topology:', error);
//             showToast('Failed to save topology', 'error');
//         }
//     }

//     getTopologyData() {
//         return {
//             devices: this.devices,
//             connections: this.connections
//         };
//     }

//     loadTopologyData(data) {
//         this.devices = data.devices || [];
//         this.connections = data.connections || [];
//         this.selectedDevice = null;
//         this.connectionStart = null;
//         this.render();
//         this.updatePropertiesPanel();
//     }

//     exportTopology() {
//         const data = this.getTopologyData();
//         const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
//         downloadFile(blob, 'topology.json');
//     }

//     importTopology(file) {
//         const reader = new FileReader();
//         reader.onload = (e) => {
//             try {
//                 const data = JSON.parse(e.target.result);
//                 this.loadTopologyData(data);
//                 showToast('Topology imported successfully', 'success');
//             } catch (error) {
//                 console.error('Failed to import topology:', error);
//                 showToast('Failed to import topology: Invalid file format', 'error');
//             }
//         };
//         reader.readAsText(file);
//     }
// }

// // Global topology builder instance
// const topologyBuilder = new TopologyBuilder();



// assets/js/api.js - API Client

class APIClient {
    constructor(baseURL = 'http://localhost:5000/api') {
        this.baseURL = baseURL;
        this.token = getLocalStorage('auth_token');
        this.refreshToken = getLocalStorage('refresh_token');
        this.isRefreshing = false;
        this.failedQueue = [];
    }

    /**
     * Set authentication token
     */
    setToken(token, refreshToken = null) {
        this.token = token;
        this.refreshToken = refreshToken;
        
        if (token) {
            setLocalStorage('auth_token', token);
            if (refreshToken) {
                setLocalStorage('refresh_token', refreshToken);
            }
        } else {
            removeLocalStorage('auth_token');
            removeLocalStorage('refresh_token');
        }
    }

    /**
     * Get authentication headers
     */
    getAuthHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (this.token) {
            headers.Authorization = `Bearer ${this.token}`;
        }
        
        return headers;
    }

    /**
     * Process failed queue after token refresh
     */
    processQueue(error, token = null) {
        this.failedQueue.forEach(({ resolve, reject }) => {
            if (error) {
                reject(error);
            } else {
                resolve(token);
            }
        });
        
        this.failedQueue = [];
    }

    /**
     * Make HTTP request with error handling and token refresh
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: this.getAuthHeaders(),
            ...options,
            headers: {
                ...this.getAuthHeaders(),
                ...options.headers
            }
        };

        try {
            const response = await fetch(url, config);
            
            // Handle 401 Unauthorized - token might be expired
            if (response.status === 401 && this.token) {
                if (!this.isRefreshing) {
                    this.isRefreshing = true;
                    
                    try {
                        await this.refreshAccessToken();
                        this.processQueue(null, this.token);
                        
                        // Retry original request with new token
                        const retryConfig = {
                            ...config,
                            headers: {
                                ...config.headers,
                                Authorization: `Bearer ${this.token}`
                            }
                        };
                        
                        const retryResponse = await fetch(url, retryConfig);
                        return await this.handleResponse(retryResponse);
                        
                    } catch (refreshError) {
                        this.processQueue(refreshError);
                        this.logout();
                        throw new Error('Session expired. Please login again.');
                    } finally {
                        this.isRefreshing = false;
                    }
                } else {
                    // If already refreshing, queue this request
                    return new Promise((resolve, reject) => {
                        this.failedQueue.push({ resolve, reject });
                    }).then(() => {
                        const retryConfig = {
                            ...config,
                            headers: {
                                ...config.headers,
                                Authorization: `Bearer ${this.token}`
                            }
                        };
                        return fetch(url, retryConfig).then(this.handleResponse);
                    });
                }
            }
            
            return await this.handleResponse(response);
            
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }

    /**
     * Handle response and parse JSON
     */
    async handleResponse(response) {
        if (!response.ok) {
            let errorMessage;
            try {
                const errorData = await response.json();
                errorMessage = errorData.message || errorData.error || `HTTP ${response.status}`;
            } catch {
                errorMessage = `HTTP ${response.status} - ${response.statusText}`;
            }
            throw new Error(errorMessage);
        }

        // Handle empty responses
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        } else {
            return response;
        }
    }

    /**
     * Refresh access token
     */
    async refreshAccessToken() {
        if (!this.refreshToken) {
            throw new Error('No refresh token available');
        }

        const response = await fetch(`${this.baseURL}/auth/refresh`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${this.refreshToken}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to refresh token');
        }

        const data = await response.json();
        this.setToken(data.access_token, data.refresh_token);
        return data.access_token;
    }

    /**
     * Logout and clear tokens
     */
    logout() {
        this.setToken(null);
        // Dispatch custom event for other parts of the app
        window.dispatchEvent(new CustomEvent('userLoggedOut'));
    }

    // ==================== AUTHENTICATION ENDPOINTS ====================

    /**
     * User login
     */
    async login(username, password) {
        const response = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
        
        this.setToken(response.access_token, response.refresh_token);
        return response;
    }

    /**
     * User registration
     */
    async register(userData) {
        return this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    /**
     * Get user profile
     */
    async getProfile() {
        return this.request('/auth/profile');
    }

    /**
     * Update user profile
     */
    async updateProfile(profileData) {
        return this.request('/auth/profile', {
            method: 'PUT',
            body: JSON.stringify(profileData)
        });
    }

    // ==================== DEVICE ENDPOINTS ====================

    /**
     * Get all devices
     */
    async getDevices() {
        return this.request('/devices');
    }

    /**
     * Get device by ID
     */
    async getDevice(id) {
        return this.request(`/devices/${id}`);
    }

    /**
     * Create new device
     */
    async createDevice(device) {
        return this.request('/devices', {
            method: 'POST',
            body: JSON.stringify(device)
        });
    }

    /**
     * Update device
     */
    async updateDevice(id, device) {
        return this.request(`/devices/${id}`, {
            method: 'PUT',
            body: JSON.stringify(device)
        });
    }

    /**
     * Delete device
     */
    async deleteDevice(id) {
        return this.request(`/devices/${id}`, {
            method: 'DELETE'
        });
    }

    /**
     * Get device ports
     */
    async getDevicePorts(deviceId) {
        return this.request(`/devices/${deviceId}/ports`);
    }

    /**
     * Create device port
     */
    async createPort(deviceId, port) {
        return this.request(`/devices/${deviceId}/ports`, {
            method: 'POST',
            body: JSON.stringify(port)
        });
    }

    /**
     * Connect two ports
     */
    async connectPorts(portId, targetPortId) {
        return this.request(`/devices/ports/${portId}/connect`, {
            method: 'POST',
            body: JSON.stringify({ target_port_id: targetPortId })
        });
    }

    /**
     * Disconnect port
     */
    async disconnectPort(portId) {
        return this.request(`/devices/ports/${portId}/disconnect`, {
            method: 'POST'
        });
    }

    // ==================== INVENTORY ENDPOINTS ====================

    /**
     * Get all inventory
     */
    async getInventory() {
        return this.request('/inventory');
    }

    /**
     * Get device inventory
     */
    async getDeviceInventory(deviceId) {
        return this.request(`/inventory/${deviceId}`);
    }

    /**
     * Update device inventory
     */
    async updateDeviceInventory(deviceId, inventoryData) {
        return this.request(`/inventory/${deviceId}`, {
            method: 'POST',
            body: JSON.stringify(inventoryData)
        });
    }

    /**
     * Scan device inventory
     */
    async scanDeviceInventory(deviceId) {
        return this.request(`/inventory/scan/${deviceId}`, {
            method: 'POST'
        });
    }

    // ==================== PROVISIONING ENDPOINTS ====================

    /**
     * Get configuration templates
     */
    async getTemplates() {
        return this.request('/provisioning/templates');
    }

    /**
     * Get template by ID
     */
    async getTemplate(id) {
        return this.request(`/provisioning/templates/${id}`);
    }

    /**
     * Create configuration template
     */
    async createTemplate(template) {
        return this.request('/provisioning/templates', {
            method: 'POST',
            body: JSON.stringify(template)
        });
    }

    /**
     * Update configuration template
     */
    async updateTemplate(id, template) {
        return this.request(`/provisioning/templates/${id}`, {
            method: 'PUT',
            body: JSON.stringify(template)
        });
    }

    /**
     * Delete configuration template
     */
    async deleteTemplate(id) {
        return this.request(`/provisioning/templates/${id}`, {
            method: 'DELETE'
        });
    }

    /**
     * Get provisioning tasks
     */
    async getProvisioningTasks() {
        return this.request('/provisioning/tasks');
    }

    /**
     * Get provisioning task by ID
     */
    async getProvisioningTask(id) {
        return this.request(`/provisioning/tasks/${id}`);
    }

    /**
     * Create provisioning task
     */
    async createProvisioningTask(task) {
        return this.request('/provisioning/tasks', {
            method: 'POST',
            body: JSON.stringify(task)
        });
    }

    /**
     * Execute provisioning task
     */
    async executeProvisioningTask(taskId) {
        return this.request(`/provisioning/execute/${taskId}`, {
            method: 'POST'
        });
    }

    // ==================== TELEMETRY ENDPOINTS ====================

    /**
     * Get telemetry configuration
     */
    async getTelemetryConfigs() {
        return this.request('/telemetry/config');
    }

    /**
     * Get device telemetry configuration
     */
    async getDeviceTelemetryConfig(deviceId) {
        return this.request(`/telemetry/config/${deviceId}`);
    }

    /**
     * Configure device telemetry
     */
    async configureTelemetry(deviceId, config) {
        return this.request(`/telemetry/config/${deviceId}`, {
            method: 'POST',
            body: JSON.stringify(config)
        });
    }

    /**
     * Get telemetry data
     */
    async getTelemetryData(deviceId, params = {}) {
        const queryString = objectToQueryString(params);
        const endpoint = queryString ? `/telemetry/data/${deviceId}?${queryString}` : `/telemetry/data/${deviceId}`;
        return this.request(endpoint);
    }

    /**
     * Collect telemetry data
     */
    async collectTelemetry(deviceId) {
        return this.request(`/telemetry/collect/${deviceId}`, {
            method: 'POST'
        });
    }

    /**
     * Get telemetry summary
     */
    async getTelemetrySummary(deviceId) {
        return this.request(`/telemetry/summary/${deviceId}`);
    }

    // ==================== REPORTS ENDPOINTS ====================

    /**
     * Get all reports
     */
    async getReports() {
        return this.request('/reports');
    }

    /**
     * Get report by ID
     */
    async getReport(id) {
        return this.request(`/reports/${id}`);
    }

    /**
     * Create report
     */
    async createReport(report) {
        return this.request('/reports', {
            method: 'POST',
            body: JSON.stringify(report)
        });
    }

    /**
     * Get report types
     */
    async getReportTypes() {
        return this.request('/reports/types');
    }

    /**
     * Download report
     */
    async downloadReport(reportId) {
        const response = await fetch(`${this.baseURL}/reports/download/${reportId}`, {
            headers: {
                Authorization: `Bearer ${this.token}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to download report');
        }
        
        return response.blob();
    }

    // ==================== TOPOLOGY ENDPOINTS ====================

    /**
     * Get topology
     */
    async getTopology(name = 'default') {
        return this.request(`/topology?name=${name}`);
    }

    /**
     * Save topology
     */
    async saveTopology(topology, name = 'default') {
        return this.request('/topology', {
            method: 'POST',
            body: JSON.stringify({ ...topology, name })
        });
    }

    /**
     * Delete topology
     */
    async deleteTopology(name) {
        return this.request(`/topology/${name}`, {
            method: 'DELETE'
        });
    }

    /**
     * Get topology list
     */
    async getTopologyList() {
        return this.request('/topology/list');
    }

    // ==================== UTILITY METHODS ====================

    /**
     * Test API connection
     */
    async testConnection() {
        try {
            const response = await fetch(`${this.baseURL}/health`);
            return response.ok;
        } catch (error) {
            console.error('API connection test failed:', error);
            return false;
        }
    }

    /**
     * Get API status
     */
    async getStatus() {
        return this.request('/status');
    }

    /**
     * Upload file
     */
    async uploadFile(file, endpoint) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${this.baseURL}${endpoint}`, {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${this.token}`
            },
            body: formData
        });

        return this.handleResponse(response);
    }

    /**
     * Bulk operations
     */
    async bulkOperation(operation, items) {
        return this.request('/bulk', {
            method: 'POST',
            body: JSON.stringify({ operation, items })
        });
    }
}

// Create global API instance
const api = new APIClient();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { APIClient, api };
}

// Listen for logout events
window.addEventListener('userLoggedOut', () => {
    // Redirect to login or refresh page
    if (window.app && window.app.showLoginScreen) {
        window.app.showLoginScreen();
    }
});

console.log('API client initialized');