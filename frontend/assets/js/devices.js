// assets/js/devices.js - Device Management

class DeviceManager {
    constructor() {
        this.devices = [];
        this.selectedDevice = null;
        this.isInitialized = false;
        this.filters = {
            type: 'all',
            status: 'all',
            search: ''
        };
        this.sortBy = 'name';
        this.sortDirection = 'asc';
        this.currentPage = 1;
        this.itemsPerPage = 10;
    }

    /**
     * Initialize device manager
     */
    async init() {
        if (this.isInitialized) return;

        console.log('Initializing device manager...');
        
        try {
            this.setupEventListeners();
            await this.loadDevices();
            this.setupFilters();
            this.isInitialized = true;
            
            console.log('Device manager initialized successfully');
        } catch (error) {
            console.error('Device manager initialization failed:', error);
            handleError(error, 'Device manager initialization');
        }
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Add device button
        $('#addDeviceBtn')?.addEventListener('click', () => this.showAddDeviceModal());
        
        // Save device button
        $('#saveDeviceBtn')?.addEventListener('click', () => this.saveDevice());
        
        // Search input
        const searchInput = $('#deviceSearch');
        if (searchInput) {
            searchInput.addEventListener('input', debounce((e) => {
                this.filters.search = e.target.value;
                this.filterAndRenderDevices();
            }, 300));
        }

        // Filter controls
        const typeFilter = $('#deviceTypeFilter');
        if (typeFilter) {
            typeFilter.addEventListener('change', (e) => {
                this.filters.type = e.target.value;
                this.filterAndRenderDevices();
            });
        }

        const statusFilter = $('#deviceStatusFilter');
        if (statusFilter) {
            statusFilter.addEventListener('change', (e) => {
                this.filters.status = e.target.value;
                this.filterAndRenderDevices();
            });
        }

        // Sort controls
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-sort]')) {
                const sortField = e.target.getAttribute('data-sort');
                this.handleSort(sortField);
            }
        });

        // Pagination
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-page]')) {
                const page = parseInt(e.target.getAttribute('data-page'));
                this.goToPage(page);
            }
        });

        // Modal close handlers
        $$('.modal-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                if (modal) this.hideModal(modal);
            });
        });

        // Form validation
        const deviceForm = $('#deviceForm');
        if (deviceForm) {
            deviceForm.addEventListener('input', (e) => {
                this.validateForm();
            });
        }
    }

    /**
     * Load devices from API
     */
    async loadDevices() {
        try {
            showLoading('#devicesTable');
            this.devices = await api.getDevices();
            this.filterAndRenderDevices();
            console.log(`Loaded ${this.devices.length} devices`);
        } catch (error) {
            console.error('Failed to load devices:', error);
            this.showErrorState();
            throw error;
        } finally {
            hideLoading('#devicesTable');
        }
    }

    /**
     * Filter and render devices based on current filters
     */
    filterAndRenderDevices() {
        let filteredDevices = [...this.devices];

        // Apply search filter
        if (this.filters.search) {
            const searchTerm = this.filters.search.toLowerCase();
            filteredDevices = filteredDevices.filter(device =>
                device.name.toLowerCase().includes(searchTerm) ||
                device.ip_address.includes(searchTerm) ||
                device.device_type.toLowerCase().includes(searchTerm)
            );
        }

        // Apply type filter
        if (this.filters.type !== 'all') {
            filteredDevices = filteredDevices.filter(device =>
                device.device_type === this.filters.type
            );
        }

        // Apply status filter
        if (this.filters.status !== 'all') {
            filteredDevices = filteredDevices.filter(device =>
                device.status === this.filters.status
            );
        }

        // Apply sorting
        filteredDevices = this.sortDevices(filteredDevices);

        // Apply pagination
        const totalItems = filteredDevices.length;
        const totalPages = Math.ceil(totalItems / this.itemsPerPage);
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const paginatedDevices = filteredDevices.slice(startIndex, startIndex + this.itemsPerPage);

        // Render devices
        this.renderDevicesTable(paginatedDevices);
        this.renderPagination(totalPages, totalItems);
        this.updateResultsInfo(filteredDevices.length, totalItems);
    }

    /**
     * Sort devices array
     */
    sortDevices(devices) {
        return sortBy(devices, this.sortBy, this.sortDirection);
    }

    /**
     * Handle table sorting
     */
    handleSort(field) {
        if (this.sortBy === field) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortBy = field;
            this.sortDirection = 'asc';
        }

        this.updateSortIndicators();
        this.filterAndRenderDevices();
    }

    /**
     * Update sort indicators in table headers
     */
    updateSortIndicators() {
        $$('[data-sort]').forEach(header => {
            header.classList.remove('sort-asc', 'sort-desc');
            if (header.getAttribute('data-sort') === this.sortBy) {
                header.classList.add(`sort-${this.sortDirection}`);
            }
        });
    }

    /**
     * Render devices table
     */
    renderDevicesTable(devices) {
        const tbody = $('#devicesTable');
        if (!tbody) return;

        tbody.innerHTML = '';

        if (devices.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-muted">
                        ${this.filters.search || this.filters.type !== 'all' || this.filters.status !== 'all' 
                            ? 'No devices match your filters' 
                            : 'No devices found. Click "Add Device" to get started.'}
                    </td>
                </tr>
            `;
            return;
        }

        devices.forEach(device => {
            const row = createElement('tr');
            row.innerHTML = `
                <td>
                    <div class="flex items-center">
                        <i class="${getDeviceIcon(device.device_type)}" 
                           style="margin-right: 12px; color: ${getDeviceTypeColor(device.device_type)};"></i>
                        <div>
                            <div class="font-medium">${device.name}</div>
                            <div class="text-sm text-muted">${device.device_type}</div>
                        </div>
                    </div>
                </td>
                <td>${device.device_type}</td>
                <td>
                    <code class="ip-address">${device.ip_address}</code>
                </td>
                <td>${getStatusBadge(device.status)}</td>
                <td>
                    <div class="flex gap-2">
                        <button class="btn btn-outline btn-sm" 
                                onclick="deviceManager.viewDevice(${device.id})"
                                title="View Details">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-outline btn-sm" 
                                onclick="deviceManager.editDevice(${device.id})"
                                title="Edit Device">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-outline btn-sm" 
                                onclick="deviceManager.connectToDevice(${device.id})"
                                title="Connect">
                            <i class="fas fa-plug"></i>
                        </button>
                        <button class="btn btn-danger btn-sm" 
                                onclick="deviceManager.deleteDevice(${device.id})"
                                title="Delete Device">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            `;

            // Add row click handler for selection
            row.addEventListener('click', (e) => {
                if (!e.target.closest('button')) {
                    this.selectDevice(device);
                }
            });

            tbody.appendChild(row);
        });
    }

    /**
     * Render pagination controls
     */
    renderPagination(totalPages, totalItems) {
        const paginationContainer = $('#devicesPagination');
        if (!paginationContainer || totalPages <= 1) {
            if (paginationContainer) paginationContainer.innerHTML = '';
            return;
        }

        let paginationHTML = '<div class="pagination">';

        // Previous button
        const prevDisabled = this.currentPage === 1 ? 'disabled' : '';
        paginationHTML += `
            <button class="btn btn-outline btn-sm ${prevDisabled}" 
                    data-page="${this.currentPage - 1}" 
                    ${prevDisabled ? 'disabled' : ''}>
                <i class="fas fa-chevron-left"></i>
            </button>
        `;

        // Page numbers
        const startPage = Math.max(1, this.currentPage - 2);
        const endPage = Math.min(totalPages, this.currentPage + 2);

        if (startPage > 1) {
            paginationHTML += `<button class="btn btn-outline btn-sm" data-page="1">1</button>`;
            if (startPage > 2) {
                paginationHTML += `<span class="pagination-ellipsis">...</span>`;
            }
        }

        for (let i = startPage; i <= endPage; i++) {
            const activeClass = i === this.currentPage ? 'btn-primary' : 'btn-outline';
            paginationHTML += `
                <button class="btn ${activeClass} btn-sm" data-page="${i}">${i}</button>
            `;
        }

        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                paginationHTML += `<span class="pagination-ellipsis">...</span>`;
            }
            paginationHTML += `<button class="btn btn-outline btn-sm" data-page="${totalPages}">${totalPages}</button>`;
        }

        // Next button
        const nextDisabled = this.currentPage === totalPages ? 'disabled' : '';
        paginationHTML += `
            <button class="btn btn-outline btn-sm ${nextDisabled}" 
                    data-page="${this.currentPage + 1}"
                    ${nextDisabled ? 'disabled' : ''}>
                <i class="fas fa-chevron-right"></i>
            </button>
        `;

        paginationHTML += '</div>';
        paginationContainer.innerHTML = paginationHTML;
    }

    /**
     * Update results information
     */
    updateResultsInfo(filteredCount, totalCount) {
        const infoContainer = $('#devicesResultsInfo');
        if (infoContainer) {
            const startItem = (this.currentPage - 1) * this.itemsPerPage + 1;
            const endItem = Math.min(this.currentPage * this.itemsPerPage, filteredCount);
            
            infoContainer.textContent = filteredCount === totalCount
                ? `Showing ${startItem}-${endItem} of ${totalCount} devices`
                : `Showing ${startItem}-${endItem} of ${filteredCount} filtered devices (${totalCount} total)`;
        }
    }

    /**
     * Go to specific page
     */
    goToPage(page) {
        this.currentPage = page;
        this.filterAndRenderDevices();
    }

    /**
     * Setup filter controls
     */
    setupFilters() {
        // Populate device type filter
        const typeFilter = $('#deviceTypeFilter');
        if (typeFilter) {
            const deviceTypes = uniqueArray(this.devices.map(d => d.device_type));
            typeFilter.innerHTML = `
                <option value="all">All Types</option>
                ${deviceTypes.map(type => 
                    `<option value="${type}">${type.charAt(0).toUpperCase() + type.slice(1)}</option>`
                ).join('')}
            `;
        }

        // Populate status filter
        const statusFilter = $('#deviceStatusFilter');
        if (statusFilter) {
            const statuses = uniqueArray(this.devices.map(d => d.status));
            statusFilter.innerHTML = `
                <option value="all">All Statuses</option>
                ${statuses.map(status => 
                    `<option value="${status}">${status.charAt(0).toUpperCase() + status.slice(1)}</option>`
                ).join('')}
            `;
        }
    }

    /**
     * Show add device modal
     */
    showAddDeviceModal() {
        this.selectedDevice = null;
        this.resetForm();
        $('#modalTitle').textContent = 'Add New Device';
        $('#saveDeviceBtn').textContent = 'Add Device';
        showModal('#addDeviceModal');
    }

    /**
     * Show edit device modal
     */
    async editDevice(id) {
        const device = this.devices.find(d => d.id === id);
        if (!device) {
            showToast('Device not found', 'error');
            return;
        }

        try {
            // Get full device details
            const fullDevice = await api.getDevice(id);
            this.selectedDevice = fullDevice;
            this.populateForm(fullDevice);
            $('#modalTitle').textContent = 'Edit Device';
            $('#saveDeviceBtn').textContent = 'Update Device';
            showModal('#addDeviceModal');
        } catch (error) {
            console.error('Failed to load device details:', error);
            showToast('Failed to load device details', 'error');
        }
    }

    /**
     * View device details
     */
    async viewDevice(id) {
        const device = this.devices.find(d => d.id === id);
        if (!device) {
            showToast('Device not found', 'error');
            return;
        }

        try {
            const fullDevice = await api.getDevice(id);
            this.showDeviceDetailsModal(fullDevice);
        } catch (error) {
            console.error('Failed to load device details:', error);
            showToast('Failed to load device details', 'error');
        }
    }

    /**
     * Show device details modal
     */
    showDeviceDetailsModal(device) {
        const modalContent = `
            <div class="device-details">
                <div class="device-header">
                    <div class="device-icon-large">
                        <i class="${getDeviceIcon(device.device_type)}"></i>
                    </div>
                    <div class="device-info">
                        <h3>${device.name}</h3>
                        <p class="device-type">${device.device_type}</p>
                        ${getStatusBadge(device.status)}
                    </div>
                </div>
                
                <div class="device-details-grid">
                    <div class="detail-item">
                        <label>IP Address</label>
                        <value><code>${device.ip_address}</code></value>
                    </div>
                    <div class="detail-item">
                        <label>SSH Port</label>
                        <value>${device.ssh_port || 22}</value>
                    </div>
                    <div class="detail-item">
                        <label>Username</label>
                        <value>${device.username || 'Not configured'}</value>
                    </div>
                    <div class="detail-item">
                        <label>Created</label>
                        <value>${formatDateTime(device.created_at)}</value>
                    </div>
                    <div class="detail-item">
                        <label>Last Updated</label>
                        <value>${formatDateTime(device.updated_at)}</value>
                    </div>
                    <div class="detail-item">
                        <label>Ports</label>
                        <value>${device.ports?.length || 0} configured</value>
                    </div>
                </div>

                ${device.ports && device.ports.length > 0 ? `
                    <div class="ports-section">
                        <h4>Port Configuration</h4>
                        <div class="ports-grid">
                            ${device.ports.map(port => `
                                <div class="port-item">
                                    <span class="port-name">${port.name}</span>
                                    <span class="port-status ${port.status}">${port.status}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;

        // Create and show modal
        const modal = createElement('div', 'modal show');
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3 class="modal-title">Device Details</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    ${modalContent}
                </div>
                <div class="modal-footer">
                    <button class="btn btn-outline modal-close">Close</button>
                    <button class="btn btn-primary" onclick="deviceManager.editDevice(${device.id})">
                        <i class="fas fa-edit"></i>
                        Edit Device
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Add close handlers
        modal.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', () => {
                modal.remove();
            });
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    /**
     * Connect to device (test connection)
     */
    async connectToDevice(id) {
        const device = this.devices.find(d => d.id === id);
        if (!device) return;

        try {
            showToast(`Connecting to ${device.name}...`, 'info');
            
            // Simulate connection test
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Random success/failure for demo
            if (Math.random() > 0.3) {
                showToast(`Successfully connected to ${device.name}`, 'success');
                
                // Update device status if it was inactive
                if (device.status === 'inactive') {
                    device.status = 'active';
                    this.filterAndRenderDevices();
                }
            } else {
                showToast(`Failed to connect to ${device.name}`, 'error');
            }
        } catch (error) {
            console.error('Connection test failed:', error);
            showToast(`Connection failed: ${error.message}`, 'error');
        }
    }

    /**
     * Delete device
     */
    async deleteDevice(id) {
        const device = this.devices.find(d => d.id === id);
        if (!device) return;

        if (!confirm(`Are you sure you want to delete "${device.name}"? This action cannot be undone.`)) {
            return;
        }

        try {
            await api.deleteDevice(id);
            this.devices = this.devices.filter(d => d.id !== id);
            this.filterAndRenderDevices();
            showToast(`Device "${device.name}" deleted successfully`, 'success');
        } catch (error) {
            console.error('Failed to delete device:', error);
            showToast('Failed to delete device: ' + error.message, 'error');
        }
    }

    /**
     * Save device (create or update)
     */
    async saveDevice() {
        const device = this.getFormData();
        
        if (!this.validateFormData(device)) {
            return;
        }

        try {
            showLoading('#saveDeviceBtn');

            if (this.selectedDevice) {
                // Update existing device
                const updatedDevice = await api.updateDevice(this.selectedDevice.id, device);
                const index = this.devices.findIndex(d => d.id === this.selectedDevice.id);
                if (index !== -1) {
                    this.devices[index] = updatedDevice;
                }
                showToast('Device updated successfully', 'success');
            } else {
                // Create new device
                const newDevice = await api.createDevice(device);
                this.devices.push(newDevice);
                showToast('Device added successfully', 'success');
            }

            this.hideModal('#addDeviceModal');
            this.filterAndRenderDevices();
            this.setupFilters(); // Refresh filters in case new types were added

        } catch (error) {
            console.error('Failed to save device:', error);
            showToast('Failed to save device: ' + error.message, 'error');
        } finally {
            hideLoading('#saveDeviceBtn');
        }
    }

    /**
     * Get form data
     */
    getFormData() {
        return {
            name: $('#deviceName')?.value?.trim(),
            device_type: $('#deviceType')?.value,
            ip_address: $('#deviceIP')?.value?.trim(),
            username: $('#deviceUsername')?.value?.trim(),
            password: $('#devicePassword')?.value,
            ssh_port: parseInt($('#deviceSSHPort')?.value) || 22
        };
    }

    /**
     * Validate form data
     */
    validateFormData(device) {
        const errors = [];

        if (!device.name) {
            errors.push('Device name is required');
        }

        if (!device.ip_address) {
            errors.push('IP address is required');
        } else if (!isValidIP(device.ip_address)) {
            errors.push('Invalid IP address format');
        }

        if (device.ssh_port && !isValidPort(device.ssh_port)) {
            errors.push('Invalid SSH port number');
        }

        // Check for duplicate IP address
        const existingDevice = this.devices.find(d => 
            d.ip_address === device.ip_address && 
            (!this.selectedDevice || d.id !== this.selectedDevice.id)
        );
        
        if (existingDevice) {
            errors.push('IP address is already in use by another device');
        }

        if (errors.length > 0) {
            showToast(errors.join('\n'), 'error');
            return false;
        }

        return true;
    }

    /**
     * Populate form with device data
     */
    populateForm(device) {
        $('#deviceName').value = device.name || '';
        $('#deviceType').value = device.device_type || 'router';
        $('#deviceIP').value = device.ip_address || '';
        $('#deviceUsername').value = device.username || '';
        $('#devicePassword').value = ''; // Don't populate password for security
        $('#deviceSSHPort').value = device.ssh_port || 22;
    }

    /**
     * Reset form
     */
    resetForm() {
        $('#deviceName').value = '';
        $('#deviceType').value = 'router';
        $('#deviceIP').value = '';
        $('#deviceUsername').value = '';
        $('#devicePassword').value = '';
        $('#deviceSSHPort').value = '22';
        this.clearFormErrors();
    }

    /**
     * Validate form in real-time
     */
    validateForm() {
        const device = this.getFormData();
        this.clearFormErrors();

        // Name validation
        if (device.name && device.name.length < 3) {
            this.showFieldError('deviceName', 'Device name must be at least 3 characters');
        }

        // IP validation
        if (device.ip_address && !isValidIP(device.ip_address)) {
            this.showFieldError('deviceIP', 'Invalid IP address format');
        }

        // Port validation
        if (device.ssh_port && !isValidPort(device.ssh_port)) {
            this.showFieldError('deviceSSHPort', 'Port must be between 1 and 65535');
        }
    }

    /**
     * Show field error
     */
    showFieldError(fieldId, message) {
        const field = $(`#${fieldId}`);
        if (field) {
            field.classList.add('error');
            
            let errorElement = field.parentNode.querySelector('.field-error');
            if (!errorElement) {
                errorElement = createElement('div', 'field-error');
                field.parentNode.appendChild(errorElement);
            }
            errorElement.textContent = message;
        }
    }

    /**
     * Clear form errors
     */
    clearFormErrors() {
        $$('.field-error').forEach(error => error.remove());
        $$('.error').forEach(field => field.classList.remove('error'));
    }

    /**
     * Hide modal
     */
    hideModal(modalSelector) {
        hideModal(modalSelector);
        this.clearFormErrors();
    }

    /**
     * Select device
     */
    selectDevice(device) {
        this.selectedDevice = device;
        
        // Update selection in table
        $$('tr').forEach(row => row.classList.remove('selected'));
        const deviceRow = $(`tr[data-device-id="${device.id}"]`);
        if (deviceRow) {
            deviceRow.classList.add('selected');
        }

        console.log('Selected device:', device.name);
    }

    /**
     * Show error state
     */
    showErrorState() {
        const tbody = $('#devicesTable');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center">
                        <div class="error-state">
                            <i class="fas fa-exclamation-triangle text-warning"></i>
                            <p>Failed to load devices</p>
                            <button class="btn btn-primary" onclick="deviceManager.loadDevices()">
                                <i class="fas fa-redo"></i>
                                Retry
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }
    }

    /**
     * Export devices data
     */
    exportDevices() {
        const exportData = this.devices.map(device => ({
            name: device.name,
            type: device.device_type,
            ip_address: device.ip_address,
            status: device.status,
            created_at: device.created_at
        }));

        downloadCSV(exportData, `network-devices-${formatDate(new Date())}.csv`);
        showToast('Devices exported successfully', 'success');
    }

    /**
     * Bulk operations
     */
    async bulkDelete(deviceIds) {
        if (!confirm(`Are you sure you want to delete ${deviceIds.length} devices?`)) {
            return;
        }

        try {
            await api.bulkOperation('delete', deviceIds);
            this.devices = this.devices.filter(d => !deviceIds.includes(d.id));
            this.filterAndRenderDevices();
            showToast(`${deviceIds.length} devices deleted successfully`, 'success');
        } catch (error) {
            console.error('Bulk delete failed:', error);
            showToast('Bulk delete failed: ' + error.message, 'error');
        }
    }

    /**
     * Get device statistics
     */
    getDeviceStats() {
        return {
            total: this.devices.length,
            byType: groupBy(this.devices, 'device_type'),
            byStatus: groupBy(this.devices, 'status'),
            active: this.devices.filter(d => d.status === 'active').length,
            inactive: this.devices.filter(d => d.status === 'inactive').length
        };
    }

    /**
     * Cleanup
     */
    destroy() {
        this.devices = [];
        this.selectedDevice = null;
        this.isInitialized = false;
        console.log('Device manager destroyed');
    }
}

// Create global device manager instance
const deviceManager = new DeviceManager();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DeviceManager, deviceManager };
}

console.log('Device manager loaded');