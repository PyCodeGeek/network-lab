// // frontend/assets/js/app.js - Main Application Controller

// class NetworkLabApp {
//     constructor() {
//         this.currentPage = 'dashboard';
//         this.pageManagers = {};
//         this.isInitialized = false;
//     }

//     async init() {
//         if (this.isInitialized) return;

//         // Check authentication status
//         const isAuthenticated = await auth.checkAuth();
        
//         if (!isAuthenticated) {
//             this.showLoginScreen();
//             return;
//         }

//         // Initialize main application
//         this.showMainApp();
//         this.setupEventListeners();
//         this.initializePageManagers();
        
//         // Show initial page
//         this.showPage('dashboard');
        
//         this.isInitialized = true;
//     }

//     showLoginScreen() {
//         showElement('#loginScreen');
//         hideElement('#mainApp');
//         this.setupLoginListeners();
//     }

//     showMainApp() {
//         hideElement('#loginScreen');
//         showElement('#mainApp');
        
//         // Update user info
//         const user = auth.getUser();
//         if (user) {
//             $('.username').textContent = user.username || 'User';
//             $('.user-role').textContent = user.role || 'User';
//         }
//     }

//     setupLoginListeners() {
//         const loginBtn = $('#loginBtn');
//         const usernameInput = $('#username');
//         const passwordInput = $('#password');

//         if (loginBtn) {
//             loginBtn.addEventListener('click', () => this.handleLogin());
//         }

//         if (passwordInput) {
//             passwordInput.addEventListener('keypress', (e) => {
//                 if (e.key === 'Enter') this.handleLogin();
//             });
//         }
//     }

//     async handleLogin() {
//         const username = $('#username')?.value?.trim();
//         const password = $('#password')?.value;
//         const loginBtn = $('#loginBtn');
//         const loginText = $('#loginText');
//         const loginSpinner = $('#loginSpinner');

//         if (!username || !password) {
//             showToast('Please enter username and password', 'error');
//             return;
//         }

//         // Show loading state
//         loginBtn.disabled = true;
//         hideElement(loginText);
//         showElement(loginSpinner);

//         try {
//             await auth.login(username, password);
//             this.showMainApp();
//             this.setupEventListeners();
//             this.initializePageManagers();
//             this.showPage('dashboard');
//             showToast('Login successful', 'success');
//         } catch (error) {
//             console.error('Login failed:', error);
//             showToast('Login failed: ' + error.message, 'error');
//         } finally {
//             loginBtn.disabled = false;
//             showElement(loginText);
//             hideElement(loginSpinner);
//         }
//     }

//     async handleLogout() {
//         if (confirm('Are you sure you want to logout?')) {
//             await auth.logout();
//             this.destroyPageManagers();
//             this.showLoginScreen();
//             showToast('Logged out successfully', 'success');
//         }
//     }

//     setupEventListeners() {
//         // Logout button
//         $('#logoutBtn')?.addEventListener('click', () => this.handleLogout());

//         // Sidebar toggle
//         $('#sidebarToggle')?.addEventListener('click', () => {
//             $('#sidebar')?.classList.toggle('collapsed');
//         });

//         // Navigation links
//         $$('.nav-link').forEach(link => {
//             link.addEventListener('click', (e) => {
//                 e.preventDefault();
//                 const page = link.getAttribute('data-page');
//                 if (page) this.showPage(page);
//             });
//         });

//         // Global modal handlers
//         $$('.modal-close').forEach(btn => {
//             btn.addEventListener('click', (e) => {
//                 const modal = e.target.closest('.modal');
//                 if (modal) hideElement(modal);
//             });
//         });

//         // Click outside modal to close
//         $$('.modal').forEach(modal => {
//             modal.addEventListener('click', (e) => {
//                 if (e.target === modal) hideElement(modal);
//             });
//         });

//         // Global keyboard shortcuts
//         document.addEventListener('keydown', (e) => {
//             // Escape to close modals
//             if (e.key === 'Escape') {
//                 const visibleModal = $('.modal.show');
//                 if (visibleModal) hideElement(visibleModal);
//             }
//         });
//     }

//     initializePageManagers() {
//         // Initialize page-specific managers
//         this.pageManagers.dashboard = new Dashboard();
//         this.pageManagers.devices = new DeviceManager();
//         this.pageManagers.topology = new TopologyBuilder();
        
//         // Initialize other managers as needed
//         // this.pageManagers.inventory = new InventoryManager();
//         // this.pageManagers.provisioning = new ProvisioningManager();
//         // this.pageManagers.telemetry = new TelemetryManager();
//         // this.pageManagers.reports = new ReportsManager();
//     }

//     destroyPageManagers() {
//         Object.values(this.pageManagers).forEach(manager => {
//             if (manager.destroy) manager.destroy();
//         });
//         this.pageManagers = {};
//     }

//     async showPage(pageId) {
//         try {
//             // Hide all pages
//             $$('.page').forEach(page => hideElement(page));

//             // Show selected page
//             showElement(`#${pageId}Page`);

//             // Update navigation
//             $$('.nav-link').forEach(link => link.classList.remove('active'));
//             $(`.nav-link[data-page="${pageId}"]`)?.classList.add('active');

//             // Update page title
//             const titles = {
//                 dashboard: 'Dashboard',
//                 topology: 'Topology Builder',
//                 devices: 'Device Management',
//                 inventory: 'Inventory Management',
//                 provisioning: 'Device Provisioning',
//                 telemetry: 'Telemetry & Monitoring',
//                 reports: 'Reports & Analytics'
//             };

//             const pageTitle = $('#pageTitle');
//             if (pageTitle) {
//                 pageTitle.textContent = titles[pageId] || 'Network Lab';
//             }

//             this.currentPage = pageId;

//             // Initialize page-specific functionality
//             await this.initializePage(pageId);

//         } catch (error) {
//             console.error(`Failed to load page ${pageId}:`, error);
//             showToast('Failed to load page', 'error');
//         }
//     }

//     async initializePage(pageId) {
//         const manager = this.pageManagers[pageId];
        
//         if (manager && manager.init && !manager.isInitialized) {
//             await manager.init();
//             manager.isInitialized = true;
//         }

//         // Page-specific initialization
//         switch (pageId) {
//             case 'dashboard':
//                 // Dashboard is automatically refreshing
//                 break;
//             case 'devices':
//                 // Device manager handles its own initialization
//                 break;
//             case 'topology':
//                 // Topology builder handles its own initialization
//                 break;
//             case 'inventory':
//                 await this.initializeInventoryPage();
//                 break;
//             case 'provisioning':
//                 await this.initializeProvisioningPage();
//                 break;
//             case 'telemetry':
//                 await this.initializeTelemetryPage();
//                 break;
//             case 'reports':
//                 await this.initializeReportsPage();
//                 break;
//         }
//     }

//     async initializeInventoryPage() {
//         // Initialize inventory page
//         const inventoryContainer = $('#inventoryPage');
//         if (!inventoryContainer) return;

//         // Add basic inventory interface
//         inventoryContainer.innerHTML = `
//             <div class="flex items-center justify-between mb-4">
//                 <h2 style="font-size: 1.5rem; font-weight: 600; margin: 0;">Network Inventory</h2>
//                 <button id="scanAllDevices" class="btn btn-primary">
//                     <i class="fas fa-search"></i>
//                     Scan All Devices
//                 </button>
//             </div>
            
//             <div class="grid grid-cols-1 gap-6">
//                 <div class="card">
//                     <div class="card-header">
//                         <h3 class="card-title">Device Inventory</h3>
//                     </div>
//                     <div class="card-body">
//                         <div id="inventoryContent">
//                             <p>Loading inventory data...</p>
//                         </div>
//                     </div>
//                 </div>
//             </div>
//         `;

//         // Setup inventory event listeners
//         $('#scanAllDevices')?.addEventListener('click', () => {
//             showToast('Scanning all devices...', 'info');
//             // Implement device scanning
//         });

//         // Load inventory data
//         this.loadInventoryData();
//     }

//     async loadInventoryData() {
//         try {
//             const devices = await api.getDevices();
//             const inventoryContent = $('#inventoryContent');
            
//             if (!inventoryContent) return;

//             const inventoryHTML = devices.map(device => `
//                 <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg mb-2">
//                     <div class="flex items-center">
//                         <i class="${getDeviceIcon(device.device_type)}" style="margin-right: 12px; color: var(--primary-color);"></i>
//                         <div>
//                             <div class="font-medium">${device.name}</div>
//                             <div class="text-sm text-gray-500">${device.ip_address}</div>
//                         </div>
//                     </div>
//                     <div class="flex items-center gap-2">
//                         ${getStatusBadge(device.status)}
//                         <button class="btn btn-outline btn-sm" onclick="app.scanDeviceInventory(${device.id})">
//                             <i class="fas fa-search"></i>
//                             Scan
//                         </button>
//                     </div>
//                 </div>
//             `).join('');

//             inventoryContent.innerHTML = inventoryHTML || '<p>No devices found</p>';
//         } catch (error) {
//             console.error('Failed to load inventory:', error);
//             const inventoryContent = $('#inventoryContent');
//             if (inventoryContent) {
//                 inventoryContent.innerHTML = '<p class="text-red-600">Failed to load inventory data</p>';
//             }
//         }
//     }

//     async scanDeviceInventory(deviceId) {
//         try {
//             showToast('Scanning device inventory...', 'info');
//             const result = await api.scanDeviceInventory(deviceId);
//             showToast('Device inventory updated', 'success');
//             console.log('Inventory result:', result);
//         } catch (error) {
//             console.error('Failed to scan device:', error);
//             showToast('Failed to scan device inventory', 'error');
//         }
//     }

//     async initializeProvisioningPage() {
//         const provisioningContainer = $('#provisioningPage');
//         if (!provisioningContainer) return;

//         provisioningContainer.innerHTML = `
//             <div class="grid grid-cols-1 gap-6">
//                 <div class="card">
//                     <div class="card-header">
//                         <h3 class="card-title">Configuration Templates</h3>
//                         <button class="btn btn-primary btn-sm">
//                             <i class="fas fa-plus"></i>
//                             Add Template
//                         </button>
//                     </div>
//                     <div class="card-body">
//                         <p>Configuration templates management will be implemented here.</p>
//                     </div>
//                 </div>
                
//                 <div class="card">
//                     <div class="card-header">
//                         <h3 class="card-title">Provisioning Tasks</h3>
//                     </div>
//                     <div class="card-body">
//                         <p>Active and completed provisioning tasks will be shown here.</p>
//                     </div>
//                 </div>
//             </div>
//         `;
//     }

//     async initializeTelemetryPage() {
//         const telemetryContainer = $('#telemetryPage');
//         if (!telemetryContainer) return;

//         telemetryContainer.innerHTML = `
//             <div class="grid grid-cols-1 gap-6">
//                 <div class="card">
//                     <div class="card-header">
//                         <h3 class="card-title">Real-time Monitoring</h3>
//                     </div>
//                     <div class="card-body">
//                         <p>Real-time device monitoring and telemetry data will be displayed here.</p>
//                     </div>
//                 </div>
                
//                 <div class="card">
//                     <div class="card-header">
//                         <h3 class="card-title">Performance Metrics</h3>
//                     </div>
//                     <div class="card-body">
//                         <p>Performance charts and metrics will be shown here.</p>
//                     </div>
//                 </div>
//             </div>
//         `;
//     }

//     async initializeReportsPage() {
//         const reportsContainer = $('#reportsPage');
//         if (!reportsContainer) return;

//         reportsContainer.innerHTML = `
//             <div class="flex items-center justify-between mb-4">
//                 <h2 style="font-size: 1.5rem; font-weight: 600; margin: 0;">Reports & Analytics</h2>
//                 <button id="generateReportBtn" class="btn btn-primary">
//                     <i class="fas fa-plus"></i>
//                     Generate Report
//                 </button>
//             </div>
            
//             <div class="grid grid-cols-1 gap-6">
//                 <div class="card">
//                     <div class="card-header">
//                         <h3 class="card-title">Available Reports</h3>
//                     </div>
//                     <div class="card-body">
//                         <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
//                             <div class="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
//                                 <i class="fas fa-chart-bar text-blue-600 mb-2" style="font-size: 1.5rem;"></i>
//                                 <h4 class="font-medium">Network Inventory</h4>
//                                 <p class="text-sm text-gray-600">Complete device and hardware inventory</p>
//                             </div>
//                             <div class="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
//                                 <i class="fas fa-chart-line text-green-600 mb-2" style="font-size: 1.5rem;"></i>
//                                 <h4 class="font-medium">Performance Report</h4>
//                                 <p class="text-sm text-gray-600">Network performance analysis</p>
//                             </div>
//                             <div class="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
//                                 <i class="fas fa-network-wired text-purple-600 mb-2" style="font-size: 1.5rem;"></i>
//                                 <h4 class="font-medium">Connectivity Report</h4>
//                                 <p class="text-sm text-gray-600">Network


// assets/js/app.js - Main Application Controller

class NetworkLabApp {
    constructor() {
        this.currentPage = 'dashboard';
        this.pageManagers = {};
        this.isInitialized = false;
        this.user = null;
        this.sidebarCollapsed = false;
    }

    /**
     * Initialize the application
     */
    async init() {
        if (this.isInitialized) return;

        console.log('Initializing Network Lab Application...');

        try {
            // Check authentication status
            const isAuthenticated = await auth.checkAuth();
            
            if (!isAuthenticated) {
                this.showLoginScreen();
                return;
            }

            // User is authenticated, show main app
            this.user = auth.getUser();
            this.showMainApp();
            this.setupEventListeners();
            this.initializePageManagers();
            
            // Show initial page
            await this.showPage('dashboard');
            
            this.isInitialized = true;
            console.log('Network Lab Application initialized successfully');

        } catch (error) {
            console.error('Application initialization failed:', error);
            handleError(error, 'Application initialization');
        }
    }

    /**
     * Show login screen
     */
    showLoginScreen() {
        showElement('#loginScreen');
        hideElement('#mainApp');
        this.setupLoginListeners();
        console.log('Login screen displayed');
    }

    /**
     * Show main application
     */
    showMainApp() {
        hideElement('#loginScreen');
        showElement('#mainApp');
        
        // Update user info in UI
        if (this.user) {
            const usernameEl = $('.username');
            const userRoleEl = $('.user-role');
            if (usernameEl) usernameEl.textContent = this.user.username || 'User';
            if (userRoleEl) userRoleEl.textContent = this.user.role || 'User';
        }

        console.log('Main application displayed');
    }

    /**
     * Setup login event listeners
     */
    setupLoginListeners() {
        const loginBtn = $('#loginBtn');
        const usernameInput = $('#username');
        const passwordInput = $('#password');

        if (loginBtn) {
            loginBtn.addEventListener('click', () => this.handleLogin());
        }

        if (passwordInput) {
            passwordInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.handleLogin();
                }
            });
        }

        if (usernameInput) {
            usernameInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    $('#password').focus();
                }
            });
        }
    }

    /**
     * Handle user login
     */
    async handleLogin() {
        const username = $('#username')?.value?.trim();
        const password = $('#password')?.value;
        const loginBtn = $('#loginBtn');
        const loginText = $('#loginText');
        const loginSpinner = $('#loginSpinner');

        if (!username || !password) {
            showToast('Please enter username and password', 'error');
            return;
        }

        try {
            // Show loading state
            loginBtn.disabled = true;
            hideElement(loginText);
            showElement(loginSpinner);

            // Attempt login
            await auth.login(username, password);
            
            this.user = auth.getUser();
            this.showMainApp();
            this.setupEventListeners();
            this.initializePageManagers();
            await this.showPage('dashboard');
            
            showToast('Login successful', 'success');
            console.log('User logged in:', this.user.username);

        } catch (error) {
            console.error('Login failed:', error);
            showToast('Login failed: ' + error.message, 'error');
            
            // Clear password field on failed login
            if ($('#password')) {
                $('#password').value = '';
                $('#password').focus();
            }

        } finally {
            // Reset login button state
            loginBtn.disabled = false;
            showElement(loginText);
            hideElement(loginSpinner);
        }
    }

    /**
     * Handle user logout
     */
    async handleLogout() {
        if (!confirm('Are you sure you want to logout?')) {
            return;
        }

        try {
            await auth.logout();
            this.destroyPageManagers();
            this.user = null;
            this.showLoginScreen();
            showToast('Logged out successfully', 'success');
            console.log('User logged out');
        } catch (error) {
            console.error('Logout failed:', error);
            showToast('Logout failed', 'error');
        }
    }

    /**
     * Setup main application event listeners
     */
    setupEventListeners() {
        // Logout button
        $('#logoutBtn')?.addEventListener('click', () => this.handleLogout());

        // Sidebar toggle
        $('#sidebarToggle')?.addEventListener('click', () => this.toggleSidebar());

        // Navigation links
        $$('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = link.getAttribute('data-page');
                if (page) {
                    this.showPage(page);
                }
            });
        });

        // Global modal handlers
        this.setupModalHandlers();

        // Global keyboard shortcuts
        this.setupKeyboardShortcuts();

        // Window events
        window.addEventListener('beforeunload', () => this.handleBeforeUnload());
        window.addEventListener('resize', debounce(() => this.handleResize(), 250));

        // Auth state changes
        auth.addListener((user) => this.handleAuthStateChange(user));

        console.log('Event listeners setup complete');
    }

    /**
     * Setup modal event handlers
     */
    setupModalHandlers() {
        // Modal close buttons
        $$('.modal-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                if (modal) {
                    hideModal('#' + modal.id);
                }
            });
        });

        // Click outside modal to close
        $$('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    hideModal('#' + modal.id);
                }
            });
        });
    }

    /**
     * Setup global keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Escape key - close modals
            if (e.key === 'Escape') {
                hideAllModals();
            }

            // Global shortcuts (only when not typing in inputs)
            if (!e.target.matches('input, textarea, select')) {
                switch (e.key) {
                    case '1':
                        if (e.ctrlKey || e.metaKey) {
                            e.preventDefault();
                            this.showPage('dashboard');
                        }
                        break;
                    case '2':
                        if (e.ctrlKey || e.metaKey) {
                            e.preventDefault();
                            this.showPage('topology');
                        }
                        break;
                    case '3':
                        if (e.ctrlKey || e.metaKey) {
                            e.preventDefault();
                            this.showPage('devices');
                        }
                        break;
                    case 'n':
                        if (e.ctrlKey || e.metaKey) {
                            e.preventDefault();
                            if (this.currentPage === 'devices') {
                                deviceManager.showAddDeviceModal();
                            }
                        }
                        break;
                    case 's':
                        if (e.ctrlKey || e.metaKey) {
                            e.preventDefault();
                            if (this.currentPage === 'topology') {
                                topologyBuilder.saveTopology();
                            }
                        }
                        break;
                }
            }
        });
    }

    /**
     * Initialize page managers
     */
    initializePageManagers() {
        console.log('Initializing page managers...');
        
        // Initialize core managers
        this.pageManagers.dashboard = dashboard;
        this.pageManagers.devices = deviceManager;
        this.pageManagers.topology = topologyBuilder;
        
        // Note: Other managers (inventory, provisioning, telemetry, reports) 
        // would be initialized here when their JS files are created
        
        console.log('Page managers initialized');
    }

    /**
     * Destroy page managers
     */
    destroyPageManagers() {
        Object.values(this.pageManagers).forEach(manager => {
            if (manager && manager.destroy) {
                manager.destroy();
            }
        });
        this.pageManagers = {};
        console.log('Page managers destroyed');
    }

    /**
     * Show specific page
     */
    async showPage(pageId) {
        if (this.currentPage === pageId) {
            return; // Already on this page
        }

        console.log(`Navigating to page: ${pageId}`);

        try {
            // Hide all pages
            $$('.page').forEach(page => hideElement(page));

            // Show selected page
            const pageElement = $(`#${pageId}Page`);
            if (!pageElement) {
                throw new Error(`Page element not found: ${pageId}Page`);
            }
            showElement(pageElement);

            // Update navigation
            $$('.nav-link').forEach(link => link.classList.remove('active'));
            const navLink = $(`.nav-link[data-page="${pageId}"]`);
            if (navLink) {
                navLink.classList.add('active');
            }

            // Update page title
            const titles = {
                dashboard: 'Dashboard',
                topology: 'Topology Builder',
                devices: 'Device Management',
                inventory: 'Inventory Management',
                provisioning: 'Device Provisioning',
                telemetry: 'Telemetry & Monitoring',
                reports: 'Reports & Analytics'
            };

            const pageTitle = $('#pageTitle');
            if (pageTitle) {
                pageTitle.textContent = titles[pageId] || 'Network Lab';
            }

            this.currentPage = pageId;

            // Initialize page-specific functionality
            await this.initializePage(pageId);

            console.log(`Successfully navigated to ${pageId}`);

        } catch (error) {
            console.error(`Failed to navigate to page ${pageId}:`, error);
            showToast('Failed to load page', 'error');
        }
    }

    /**
     * Initialize specific page
     */
    async initializePage(pageId) {
        const manager = this.pageManagers[pageId];
        
        if (manager && manager.init && !manager.isInitialized) {
            try {
                await manager.init();
                console.log(`${pageId} manager initialized`);
            } catch (error) {
                console.error(`Failed to initialize ${pageId} manager:`, error);
                throw error;
            }
        }

        // Page-specific initialization
        switch (pageId) {
            case 'dashboard':
                // Dashboard auto-initializes
                break;
            case 'devices':
                // Device manager auto-initializes
                break;
            case 'topology':
                // Topology builder auto-initializes
                break;
            case 'inventory':
                await this.initializeInventoryPage();
                break;
            case 'provisioning':
                await this.initializeProvisioningPage();
                break;
            case 'telemetry':
                await this.initializeTelemetryPage();
                break;
            case 'reports':
                await this.initializeReportsPage();
                break;
        }
    }

    /**
     * Initialize inventory page (placeholder)
     */
    async initializeInventoryPage() {
        const container = $('#inventoryPage');
        if (!container || container.innerHTML.trim()) return;

        container.innerHTML = `
            <div class="page-header">
                <h2>Network Inventory</h2>
                <button id="scanAllDevices" class="btn btn-primary">
                    <i class="fas fa-search"></i>
                    Scan All Devices
                </button>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Device Inventory</h3>
                </div>
                <div class="card-body">
                    <div id="inventoryContent">
                        <p>Loading inventory data...</p>
                    </div>
                </div>
            </div>
        `;

        // Setup event listeners
        $('#scanAllDevices')?.addEventListener('click', () => {
            showToast('Scanning all devices...', 'info');
            // Implementation would go here
        });

        // Load inventory data
        setTimeout(() => {
            this.loadInventoryData();
        }, 500);
    }

    /**
     * Load inventory data (placeholder)
     */
    async loadInventoryData() {
        try {
            const devices = await api.getDevices();
            const inventoryContent = $('#inventoryContent');
            
            if (!inventoryContent) return;

            const inventoryHTML = devices.map(device => `
                <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg mb-2">
                    <div class="flex items-center">
                        <i class="${getDeviceIcon(device.device_type)}" style="margin-right: 12px; color: var(--primary-color);"></i>
                        <div>
                            <div class="font-medium">${device.name}</div>
                            <div class="text-sm text-muted">${device.ip_address}</div>
                        </div>
                    </div>
                    <div class="flex items-center gap-2">
                        ${getStatusBadge(device.status)}
                        <button class="btn btn-outline btn-sm" onclick="app.scanDeviceInventory(${device.id})">
                            <i class="fas fa-search"></i>
                            Scan
                        </button>
                    </div>
                </div>
            `).join('');

            inventoryContent.innerHTML = inventoryHTML || '<p>No devices found</p>';
        } catch (error) {
            console.error('Failed to load inventory:', error);
            const inventoryContent = $('#inventoryContent');
            if (inventoryContent) {
                inventoryContent.innerHTML = '<p class="text-red">Failed to load inventory data</p>';
            }
        }
    }

    /**
     * Initialize provisioning page (placeholder)
     */
    async initializeProvisioningPage() {
        const container = $('#provisioningPage');
        if (!container || container.innerHTML.trim()) return;

        container.innerHTML = `
            <div class="page-header">
                <h2>Device Provisioning</h2>
                <button class="btn btn-primary">
                    <i class="fas fa-plus"></i>
                    New Template
                </button>
            </div>
            
            <div class="cards-grid">
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">Configuration Templates</h3>
                    </div>
                    <div class="card-body">
                        <p>Configuration templates management will be implemented here.</p>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">Provisioning Tasks</h3>
                    </div>
                    <div class="card-body">
                        <p>Active and completed provisioning tasks will be shown here.</p>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Initialize telemetry page (placeholder)
     */
    async initializeTelemetryPage() {
        const container = $('#telemetryPage');
        if (!container || container.innerHTML.trim()) return;

        container.innerHTML = `
            <div class="page-header">
                <h2>Telemetry & Monitoring</h2>
                <button class="btn btn-primary">
                    <i class="fas fa-chart-line"></i>
                    View Analytics
                </button>
            </div>
            
            <div class="cards-grid">
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">Real-time Monitoring</h3>
                    </div>
                    <div class="card-body">
                        <p>Real-time device monitoring and telemetry data will be displayed here.</p>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">Performance Metrics</h3>
                    </div>
                    <div class="card-body">
                        <p>Performance charts and metrics will be shown here.</p>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Initialize reports page (placeholder)
     */
    async initializeReportsPage() {
        const container = $('#reportsPage');
        if (!container || container.innerHTML.trim()) return;

        container.innerHTML = `
            <div class="page-header">
                <h2>Reports & Analytics</h2>
                <button id="generateReportBtn" class="btn btn-primary">
                    <i class="fas fa-plus"></i>
                    Generate Report
                </button>
            </div>
            
            <div class="cards-grid">
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">Available Reports</h3>
                    </div>
                    <div class="card-body">
                        <div class="report-types">
                            <div class="report-type-card">
                                <i class="fas fa-chart-bar text-blue"></i>
                                <h4>Network Inventory</h4>
                                <p>Complete device and hardware inventory</p>
                            </div>
                            <div class="report-type-card">
                                <i class="fas fa-chart-line text-green"></i>
                                <h4>Performance Report</h4>
                                <p>Network performance analysis</p>
                            </div>
                            <div class="report-type-card">
                                <i class="fas fa-network-wired text-purple"></i>
                                <h4>Connectivity Report</h4>
                                <p>Network topology and connections</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">Recent Reports</h3>
                    </div>
                    <div class="card-body">
                        <div id="recentReportsList">
                            <p>Loading recent reports...</p>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Setup report generation
        $('#generateReportBtn')?.addEventListener('click', () => {
            showToast('Report generation feature coming soon!', 'info');
        });

        // Load recent reports
        setTimeout(() => {
            this.loadRecentReports();
        }, 500);
    }

    /**
     * Load recent reports (placeholder)
     */
    async loadRecentReports() {
        const recentReportsList = $('#recentReportsList');
        if (recentReportsList) {
            recentReportsList.innerHTML = `
                <div class="space-y-3">
                    <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                            <div class="font-medium">Weekly Network Inventory</div>
                            <div class="text-sm text-muted">Generated: ${formatDate(new Date())}</div>
                        </div>
                        <div class="flex items-center gap-2">
                            <span class="badge badge-success">Completed</span>
                            <button class="btn btn-outline btn-sm">
                                <i class="fas fa-download"></i>
                                Download
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }
    }

    /**
     * Toggle sidebar collapsed state
     */
    toggleSidebar() {
        this.sidebarCollapsed = !this.sidebarCollapsed;
        const sidebar = $('#sidebar');
        if (sidebar) {
            sidebar.classList.toggle('collapsed', this.sidebarCollapsed);
        }
        
        // Save preference
        setLocalStorage('sidebarCollapsed', this.sidebarCollapsed);
    }

    /**
     * Handle authentication state changes
     */
    handleAuthStateChange(user) {
        if (!user && this.isInitialized) {
            // User logged out
            this.destroyPageManagers();
            this.showLoginScreen();
        }
    }

    /**
     * Handle window resize
     */
    handleResize() {
        // Update topology canvas if active
        if (this.currentPage === 'topology' && topologyBuilder.updateCanvasRect) {
            topologyBuilder.updateCanvasRect();
        }
    }

    /**
     * Handle before window unload
     */
    handleBeforeUnload() {
        // Save any unsaved changes
        if (this.currentPage === 'topology' && topologyBuilder.saveTopology) {
            try {
                topologyBuilder.saveTopology();
            } catch (error) {
                console.error('Failed to save topology on unload:', error);
            }
        }
    }

    /**
     * Scan device inventory
     */
    async scanDeviceInventory(deviceId) {
        try {
            showToast('Scanning device inventory...', 'info');
            const result = await api.scanDeviceInventory(deviceId);
            showToast('Device inventory updated', 'success');
            console.log('Inventory result:', result);
        } catch (error) {
            console.error('Failed to scan device:', error);
            showToast('Failed to scan device inventory', 'error');
        }
    }

    /**
     * Get current page
     */
    getCurrentPage() {
        return this.currentPage;
    }

    /**
     * Get page manager
     */
    getPageManager(pageId) {
        return this.pageManagers[pageId];
    }

    /**
     * Get application status
     */
    getAppStatus() {
        return {
            isInitialized: this.isInitialized,
            currentPage: this.currentPage,
            user: this.user,
            isAuthenticated: auth.isAuthenticated(),
            pageManagers: Object.keys(this.pageManagers),
            sidebarCollapsed: this.sidebarCollapsed
        };
    }

    /**
     * Global error handler
     */
    handleError(error, context = '') {
        console.error(`Error in ${context}:`, error);
        showToast(`Error: ${error.message}`, 'error');
    }

    /**
     * Cleanup application
     */
    destroy() {
        this.destroyPageManagers();
        this.isInitialized = false;
        this.user = null;
        console.log('Application destroyed');
    }
}

// Create global app instance
const app = new NetworkLabApp();

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    app.init().catch(error => {
        console.error('Failed to initialize application:', error);
        showToast('Failed to initialize application', 'error');
    });
});

// Global error handler for unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    showToast('An unexpected error occurred', 'error');
});

// Export for global access
window.app = app;

// Debug helpers (only in development)
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    window.debugApp = () => {
        console.log('App Status:', app.getAppStatus());
        console.log('Auth Status:', auth.getAuthState());
        if (dashboard) console.log('Dashboard Status:', dashboard.getStatus());
        if (deviceManager) console.log('Device Manager Stats:', deviceManager.getDeviceStats());
        if (topologyBuilder) console.log('Topology Stats:', topologyBuilder.getTopologyStats());
    };
    
    console.log('Debug helper available: window.debugApp()');
}

console.log('Network Lab Application loaded');