// assets/js/dashboard.js - Dashboard Management

class Dashboard {
    constructor() {
        this.refreshInterval = null;
        this.charts = {};
        this.widgets = {};
        this.isInitialized = false;
        this.refreshRate = 32320; // 30 seconds
        this.data = {
            devices: [],
            telemetry: {},
            systemHealth: {},
            alerts: []
        };
    }

    /**
     * Initialize dashboard
     */
    async init() {
        if (this.isInitialized) return;

        console.log('Initializing dashboard...');
        
        try {
            await this.loadInitialData();
            this.setupEventListeners();
            this.startAutoRefresh();
            this.isInitialized = true;
            
            console.log('Dashboard initialized successfully');
        } catch (error) {
            console.error('Dashboard initialization failed:', error);
            handleError(error, 'Dashboard initialization');
        }
    }

    /**
     * Load initial dashboard data
     */
    async loadInitialData() {
        await Promise.all([
            this.loadDeviceStats(),
            this.loadRecentDevices(),
            this.loadSystemHealth(),
            this.loadRecentAlerts()
        ]);
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Refresh button click
        const refreshBtn = $('#dashboardRefresh');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshDashboard());
        }

        // Widget actions
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-widget-action]')) {
                const action = e.target.getAttribute('data-widget-action');
                const widget = e.target.getAttribute('data-widget');
                this.handleWidgetAction(widget, action);
            }
        });

        // Auto-refresh toggle
        const autoRefreshToggle = $('#autoRefresh');
        if (autoRefreshToggle) {
            autoRefreshToggle.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.startAutoRefresh();
                } else {
                    this.stopAutoRefresh();
                }
            });
        }
    }

    /**
     * Load device statistics
     */
    async loadDeviceStats() {
        try {
            const devices = await api.getDevices();
            this.data.devices = devices;

            const totalDevices = devices.length;
            const activeDevices = devices.filter(d => d.status === 'active').length;
            const inactiveDevices = devices.filter(d => d.status === 'inactive').length;
            const warningDevices = devices.filter(d => d.status === 'warning').length;

            // Update stat cards
            this.updateStatCard('totalDevices', totalDevices);
            this.updateStatCard('activeDevices', activeDevices);
            this.updateStatCard('inactiveDevices', inactiveDevices);
            this.updateStatCard('warningDevices', warningDevices);

            // Update device type breakdown
            this.updateDeviceTypeBreakdown(devices);

        } catch (error) {
            console.error('Failed to load device stats:', error);
            this.showErrorState('deviceStats');
        }
    }

    /**
     * Update stat card value
     */
    updateStatCard(cardId, value) {
        const element = $(`#${cardId}`);
        if (element) {
            const currentValue = parseInt(element.textContent) || 0;
            if (currentValue !== value) {
                animateValue(currentValue, value, 1000, (current) => {
                    element.textContent = Math.round(current);
                });
            }
        }
    }

    /**
     * Update device type breakdown
     */
    updateDeviceTypeBreakdown(devices) {
        const breakdown = groupBy(devices, 'device_type');
        const breakdownContainer = $('#deviceTypeBreakdown');
        
        if (breakdownContainer) {
            const html = Object.entries(breakdown).map(([type, devices]) => `
                <div class="device-type-item">
                    <div class="device-type-icon">
                        <i class="${getDeviceIcon(type)}"></i>
                    </div>
                    <div class="device-type-info">
                        <span class="device-type-name">${type.charAt(0).toUpperCase() + type.slice(1)}</span>
                        <span class="device-type-count">${devices.length}</span>
                    </div>
                </div>
            `).join('');
            
            breakdownContainer.innerHTML = html;
        }
    }

    /**
     * Load recent devices table
     */
    async loadRecentDevices() {
        try {
            const devices = this.data.devices.length > 0 ? this.data.devices : await api.getDevices();
            const recentDevices = devices
                .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
                .slice(0, 5);

            const tbody = $('#recentDevicesTable');
            if (!tbody) return;

            tbody.innerHTML = '';

            if (recentDevices.length === 0) {
                tbody.innerHTML = '<tr><td colspan="3" class="text-center text-muted">No devices found</td></tr>';
                return;
            }

            recentDevices.forEach(device => {
                const row = createElement('tr');
                row.innerHTML = `
                    <td>
                        <div class="flex items-center">
                            <i class="${getDeviceIcon(device.device_type)}" style="margin-right: 8px; color: var(--primary-color);"></i>
                            <div>
                                <div class="font-medium">${device.name}</div>
                                <div class="text-sm text-muted">${device.ip_address}</div>
                            </div>
                        </div>
                    </td>
                    <td style="text-transform: capitalize;">${device.device_type}</td>
                    <td>${getStatusBadge(device.status)}</td>
                `;
                
                // Add click handler to navigate to device details
                row.addEventListener('click', () => {
                    this.navigateToDevice(device.id);
                });
                
                row.style.cursor = 'pointer';
                tbody.appendChild(row);
            });

        } catch (error) {
            console.error('Failed to load recent devices:', error);
            this.showErrorState('recentDevices');
        }
    }

    /**
     * Load system health metrics
     */
    async loadSystemHealth() {
        try {
            // In a real application, this would come from system monitoring APIs
            const healthData = await this.generateSystemHealthData();
            this.data.systemHealth = healthData;

            const healthContainer = $('#systemHealth');
            if (!healthContainer) return;

            const healthHtml = healthData.map(metric => {
                let badgeClass = 'badge-success';
                let iconClass = 'fas fa-check-circle text-green';
                
                if (typeof metric.value === 'number') {
                    if (metric.value > 80) {
                        badgeClass = 'badge-danger';
                        iconClass = 'fas fa-exclamation-triangle text-red';
                    } else if (metric.value > 60) {
                        badgeClass = 'badge-warning';
                        iconClass = 'fas fa-exclamation-circle text-yellow';
                    }
                }

                const displayValue = typeof metric.value === 'number' 
                    ? `${Math.round(metric.value)}${metric.unit}`
                    : metric.value;

                return `
                    <div class="health-metric">
                        <div class="flex items-center">
                            <i class="${iconClass}" style="margin-right: 8px;"></i>
                            <span>${metric.name}</span>
                        </div>
                        <span class="badge ${badgeClass}">${displayValue}</span>
                    </div>
                `;
            }).join('');

            healthContainer.innerHTML = healthHtml;

        } catch (error) {
            console.error('Failed to load system health:', error);
            this.showErrorState('systemHealth');
        }
    }

    /**
     * Generate simulated system health data
     */
    async generateSystemHealthData() {
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 200));

        return [
            {
                name: 'CPU Usage',
                value: randomBetween(15, 75),
                unit: '%',
                threshold: 80
            },
            {
                name: 'Memory Usage',
                value: randomBetween(30, 85),
                unit: '%',
                threshold: 85
            },
            {
                name: 'Disk Usage',
                value: randomBetween(40, 90),
                unit: '%',
                threshold: 90
            },
            {
                name: 'Network Traffic',
                value: 'Normal',
                unit: '',
                status: 'healthy'
            },
            {
                name: 'Database',
                value: 'Connected',
                unit: '',
                status: 'healthy'
            },
            {
                name: 'API Response',
                value: randomBetween(50, 200),
                unit: 'ms',
                threshold: 500
            }
        ];
    }

    /**
     * Load recent alerts
     */
    async loadRecentAlerts() {
        try {
            // Simulate alerts for demo
            const alerts = await this.generateAlerts();
            this.data.alerts = alerts;

            const alertsContainer = $('#recentAlerts');
            if (!alertsContainer) return;

            if (alerts.length === 0) {
                alertsContainer.innerHTML = '<p class="text-muted text-center">No recent alerts</p>';
                return;
            }

            const alertsHtml = alerts.slice(0, 5).map(alert => `
                <div class="alert-item ${alert.severity}">
                    <div class="alert-icon">
                        <i class="${this.getAlertIcon(alert.severity)}"></i>
                    </div>
                    <div class="alert-content">
                        <div class="alert-message">${alert.message}</div>
                        <div class="alert-time">${formatRelativeTime(alert.timestamp)}</div>
                    </div>
                </div>
            `).join('');

            alertsContainer.innerHTML = alertsHtml;

        } catch (error) {
            console.error('Failed to load alerts:', error);
            this.showErrorState('alerts');
        }
    }

    /**
     * Generate sample alerts
     */
    async generateAlerts() {
        const alertTypes = [
            { message: 'Device Router-01 is unreachable', severity: 'critical' },
            { message: 'High CPU usage on Switch-02', severity: 'warning' },
            { message: 'New device discovered: Server-03', severity: 'info' },
            { message: 'Backup completed successfully', severity: 'success' },
            { message: 'Configuration sync failed for Router-04', severity: 'error' }
        ];

        return alertTypes.map((alert, index) => ({
            id: index + 1,
            ...alert,
            timestamp: new Date(Date.now() - (index * 3600000)) // Hours ago
        }));
    }

    /**
     * Get alert icon based on severity
     */
    getAlertIcon(severity) {
        const icons = {
            critical: 'fas fa-exclamation-triangle',
            error: 'fas fa-times-circle',
            warning: 'fas fa-exclamation-circle',
            info: 'fas fa-info-circle',
            success: 'fas fa-check-circle'
        };
        return icons[severity] || 'fas fa-bell';
    }

    /**
     * Load network performance data
     */
    async loadNetworkPerformance() {
        try {
            // In a real app, this would fetch actual performance metrics
            const performanceData = await this.generatePerformanceData();
            this.updatePerformanceChart(performanceData);
        } catch (error) {
            console.error('Failed to load network performance:', error);
        }
    }

    /**
     * Generate sample performance data
     */
    async generatePerformanceData() {
        const now = new Date();
        const data = [];
        
        for (let i = 23; i >= 0; i--) {
            const time = new Date(now.getTime() - (i * 3600000));
            data.push({
                time: time.toISOString(),
                throughput: randomBetween(50, 950),
                latency: randomBetween(10, 100),
                packetLoss: randomBetween(0, 5)
            });
        }
        
        return data;
    }

    /**
     * Update performance chart (placeholder for chart library)
     */
    updatePerformanceChart(data) {
        const chartContainer = $('#performanceChart');
        if (!chartContainer) return;

        // Simple text-based chart for demo (replace with actual chart library)
        const latestData = data[data.length - 1];
        chartContainer.innerHTML = `
            <div class="performance-summary">
                <div class="performance-metric">
                    <span class="metric-label">Throughput</span>
                    <span class="metric-value">${Math.round(latestData.throughput)} Mbps</span>
                </div>
                <div class="performance-metric">
                    <span class="metric-label">Latency</span>
                    <span class="metric-value">${Math.round(latestData.latency)} ms</span>
                </div>
                <div class="performance-metric">
                    <span class="metric-label">Packet Loss</span>
                    <span class="metric-value">${latestData.packetLoss.toFixed(2)}%</span>
                </div>
            </div>
        `;
    }

    /**
     * Load topology summary
     */
    async loadTopologySummary() {
        try {
            // This would typically fetch topology data from API
            const devices = this.data.devices;
            const summary = {
                totalConnections: Math.floor(devices.length * 1.5),
                redundantPaths: Math.floor(devices.length * 0.3),
                isolatedDevices: devices.filter(d => d.status === 'inactive').length
            };

            this.updateTopologySummary(summary);
        } catch (error) {
            console.error('Failed to load topology summary:', error);
        }
    }

    /**
     * Update topology summary display
     */
    updateTopologySummary(summary) {
        const container = $('#topologySummary');
        if (!container) return;

        container.innerHTML = `
            <div class="topology-stats">
                <div class="topology-stat">
                    <i class="fas fa-link text-blue"></i>
                    <span>${summary.totalConnections} Connections</span>
                </div>
                <div class="topology-stat">
                    <i class="fas fa-route text-green"></i>
                    <span>${summary.redundantPaths} Redundant Paths</span>
                </div>
                <div class="topology-stat">
                    <i class="fas fa-unlink text-red"></i>
                    <span>${summary.isolatedDevices} Isolated</span>
                </div>
            </div>
        `;
    }

    /**
     * Start auto-refresh timer
     */
    startAutoRefresh() {
        this.stopAutoRefresh();
        this.refreshInterval = setInterval(() => {
            this.refreshDashboard();
        }, this.refreshRate);
        
        console.log(`Auto-refresh started (${this.refreshRate / 1000}s interval)`);
    }

    /**
     * Stop auto-refresh timer
     */
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
            console.log('Auto-refresh stopped');
        }
    }

    /**
     * Manually refresh dashboard
     */
    async refreshDashboard() {
        console.log('Refreshing dashboard...');
        
        try {
            await this.loadInitialData();
            this.updateLastRefreshTime();
            console.log('Dashboard refreshed successfully');
        } catch (error) {
            console.error('Dashboard refresh failed:', error);
            showToast('Failed to refresh dashboard', 'error');
        }
    }

    /**
     * Update last refresh time display
     */
    updateLastRefreshTime() {
        const timeElement = $('#lastRefreshTime');
        if (timeElement) {
            timeElement.textContent = `Last updated: ${formatTime(new Date())}`;
        }
    }

    /**
     * Handle widget actions
     */
    handleWidgetAction(widget, action) {
        switch (action) {
            case 'refresh':
                this.refreshWidget(widget);
                break;
            case 'expand':
                this.expandWidget(widget);
                break;
            case 'settings':
                this.showWidgetSettings(widget);
                break;
            default:
                console.log(`Unknown widget action: ${action}`);
        }
    }

    /**
     * Refresh specific widget
     */
    async refreshWidget(widget) {
        console.log(`Refreshing widget: ${widget}`);
        
        try {
            switch (widget) {
                case 'deviceStats':
                    await this.loadDeviceStats();
                    break;
                case 'recentDevices':
                    await this.loadRecentDevices();
                    break;
                case 'systemHealth':
                    await this.loadSystemHealth();
                    break;
                case 'alerts':
                    await this.loadRecentAlerts();
                    break;
                case 'performance':
                    await this.loadNetworkPerformance();
                    break;
                case 'topology':
                    await this.loadTopologySummary();
                    break;
                default:
                    console.log(`Unknown widget: ${widget}`);
            }
            showToast(`${widget} updated`, 'success');
        } catch (error) {
            console.error(`Failed to refresh widget ${widget}:`, error);
            showToast(`Failed to refresh ${widget}`, 'error');
        }
    }

    /**
     * Navigate to device details
     */
    navigateToDevice(deviceId) {
        if (window.app && window.app.showPage) {
            // Store selected device ID for device management page
            sessionStorage.setItem('selectedDeviceId', deviceId);
            window.app.showPage('devices');
        }
    }

    /**
     * Navigate to topology builder
     */
    navigateToTopology() {
        if (window.app && window.app.showPage) {
            window.app.showPage('topology');
        }
    }

    /**
     * Show error state for widget
     */
    showErrorState(widget) {
        const container = $(`#${widget}`);
        if (container) {
            container.innerHTML = `
                <div class="error-state">
                    <i class="fas fa-exclamation-triangle text-warning"></i>
                    <p>Failed to load ${widget}</p>
                    <button class="btn btn-sm btn-outline" onclick="dashboard.refreshWidget('${widget}')">
                        <i class="fas fa-redo"></i>
                        Retry
                    </button>
                </div>
            `;
        }
    }

    /**
     * Load dashboard widgets based on user preferences
     */
    loadUserDashboard() {
        const userPrefs = getLocalStorage('dashboardPrefs', {
            widgets: ['deviceStats', 'recentDevices', 'systemHealth', 'alerts'],
            layout: 'default',
            refreshRate: 32320
        });

        this.refreshRate = userPrefs.refreshRate;
        // Apply user preferences for widget visibility, layout, etc.
    }

    /**
     * Save dashboard preferences
     */
    saveDashboardPrefs(prefs) {
        const currentPrefs = getLocalStorage('dashboardPrefs', {});
        const newPrefs = { ...currentPrefs, ...prefs };
        setLocalStorage('dashboardPrefs', newPrefs);
    }

    /**
     * Export dashboard data
     */
    exportDashboardData() {
        const exportData = {
            timestamp: new Date().toISOString(),
            devices: this.data.devices,
            systemHealth: this.data.systemHealth,
            alerts: this.data.alerts,
            summary: {
                totalDevices: this.data.devices.length,
                activeDevices: this.data.devices.filter(d => d.status === 'active').length,
                inactiveDevices: this.data.devices.filter(d => d.status === 'inactive').length
            }
        };

        downloadJSON(exportData, `network-lab-dashboard-${formatDate(new Date())}.json`);
        showToast('Dashboard data exported', 'success');
    }

    /**
     * Get dashboard summary for reports
     */
    getDashboardSummary() {
        return {
            totalDevices: this.data.devices.length,
            devicesByType: groupBy(this.data.devices, 'device_type'),
            devicesByStatus: groupBy(this.data.devices, 'status'),
            systemHealth: this.data.systemHealth,
            alertsSummary: {
                total: this.data.alerts.length,
                critical: this.data.alerts.filter(a => a.severity === 'critical').length,
                warnings: this.data.alerts.filter(a => a.severity === 'warning').length
            },
            lastUpdated: new Date().toISOString()
        };
    }

    /**
     * Setup real-time updates (WebSocket placeholder)
     */
    setupRealTimeUpdates() {
        // Placeholder for WebSocket connection
        // In a real application, you would connect to a WebSocket server
        console.log('Real-time updates would be configured here');
    }

    /**
     * Cleanup dashboard resources
     */
    destroy() {
        this.stopAutoRefresh();
        
        // Clear any charts
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.destroy) {
                chart.destroy();
            }
        });
        
        this.charts = {};
        this.widgets = {};
        this.isInitialized = false;
        
        console.log('Dashboard destroyed');
    }

    /**
     * Get dashboard status
     */
    getStatus() {
        return {
            isInitialized: this.isInitialized,
            isAutoRefreshing: !!this.refreshInterval,
            refreshRate: this.refreshRate,
            lastRefresh: this.lastRefresh,
            dataLoadTime: this.dataLoadTime,
            widgets: Object.keys(this.widgets),
            errors: this.errors || []
        };
    }
}

// Create global dashboard instance
const dashboard = new Dashboard();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { Dashboard, dashboard };
}

console.log('Dashboard manager loaded');