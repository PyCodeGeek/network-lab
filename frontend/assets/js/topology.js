// assets/js/topology.js - Topology Builder

class TopologyBuilder {
    constructor() {
        this.devices = [];
        this.connections = [];
        this.selectedDevice = null;
        this.selectedConnection = null;
        this.currentTool = 'select';
        this.connectionStart = null;
        this.deviceCounter = 1;
        this.canvas = null;
        this.canvasRect = null;
        this.isDragging = false;
        this.draggedDevice = null;
        this.draggedDeviceType = null;
        this.isInitialized = false;
        this.gridSize = 20;
        this.snapToGrid = true;
        this.history = [];
        this.historyIndex = -1;
        this.maxHistory = 50;
    }

    /**
     * Initialize topology builder
     */
    async init() {
        if (this.isInitialized) return;

        console.log('Initializing topology builder...');
        
        try {
            this.canvas = $('#topologyCanvas');
            if (!this.canvas) {
                throw new Error('Topology canvas not found');
            }

            this.setupEventListeners();
            this.setupDragAndDrop();
            this.updateCanvasRect();
            await this.loadTopology();
            this.render();
            this.saveState();
            this.isInitialized = true;
            
            console.log('Topology builder initialized successfully');
        } catch (error) {
            console.error('Topology builder initialization failed:', error);
            handleError(error, 'Topology builder initialization');
        }
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Tool buttons
        $('#selectTool')?.addEventListener('click', () => this.setTool('select'));
        $('#connectTool')?.addEventListener('click', () => this.setTool('connect'));
        $('#clearCanvas')?.addEventListener('click', () => this.clearCanvas());

        // Canvas events
        this.canvas?.addEventListener('click', (e) => this.handleCanvasClick(e));
        this.canvas?.addEventListener('contextmenu', (e) => this.handleCanvasRightClick(e));

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));

        // Save/Load buttons
        $('#saveTopology')?.addEventListener('click', () => this.saveTopology());
        $('#loadTopology')?.addEventListener('click', () => this.loadTopologyDialog());
        $('#exportTopology')?.addEventListener('click', () => this.exportTopology());
        $('#importTopology')?.addEventListener('click', () => this.importTopologyDialog());

        // Canvas resize handler
        window.addEventListener('resize', debounce(() => {
            this.updateCanvasRect();
        }, 250));

        // Grid toggle
        $('#gridToggle')?.addEventListener('change', (e) => {
            this.snapToGrid = e.target.checked;
        });

        // Zoom controls
        $('#zoomIn')?.addEventListener('click', () => this.zoomIn());
        $('#zoomOut')?.addEventListener('click', () => this.zoomOut());
        $('#zoomReset')?.addEventListener('click', () => this.resetZoom());
    }

    /**
     * Setup drag and drop functionality
     */
    setupDragAndDrop() {
        // Handle device palette drag start
        $$('.device-item').forEach(item => {
            item.addEventListener('dragstart', (e) => {
                this.draggedDeviceType = e.target.closest('.device-item').getAttribute('data-device-type');
                e.dataTransfer.effectAllowed = 'copy';
                
                // Visual feedback
                e.target.style.opacity = '0.5';
            });

            item.addEventListener('dragend', (e) => {
                e.target.style.opacity = '';
            });
        });

        // Canvas drop handlers
        this.canvas?.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'copy';
            this.canvas.classList.add('drag-over');
        });

        this.canvas?.addEventListener('dragleave', (e) => {
            if (!this.canvas.contains(e.relatedTarget)) {
                this.canvas.classList.remove('drag-over');
            }
        });

        this.canvas?.addEventListener('drop', (e) => {
            e.preventDefault();
            this.canvas.classList.remove('drag-over');
            this.handleDrop(e);
        });
    }

    /**
     * Handle device drop on canvas
     */
    handleDrop(e) {
        if (!this.draggedDeviceType) return;

        const rect = this.canvas.getBoundingClientRect();
        let x = e.clientX - rect.left - 40; // Center the device
        let y = e.clientY - rect.top - 40;

        // Snap to grid if enabled
        if (this.snapToGrid) {
            x = Math.round(x / this.gridSize) * this.gridSize;
            y = Math.round(y / this.gridSize) * this.gridSize;
        }

        // Ensure device stays within canvas bounds
        x = Math.max(0, Math.min(x, rect.width - 80));
        y = Math.max(0, Math.min(y, rect.height - 80));

        const device = {
            id: Date.now(),
            name: this.generateDeviceName(this.draggedDeviceType),
            type: this.draggedDeviceType,
            x: x,
            y: y,
            ports: this.generatePortsForDevice(this.draggedDeviceType)
        };

        this.devices.push(device);
        this.render();
        this.updateCanvasStatus(`${device.name} added to topology`);
        this.saveState();

        this.draggedDeviceType = null;
    }

    /**
     * Generate device name based on type
     */
    generateDeviceName(type) {
        const prefix = type.charAt(0).toUpperCase() + type.slice(1);
        let counter = 1;
        let name;
        
        do {
            name = `${prefix}-${counter.toString().padStart(2, '0')}`;
            counter++;
        } while (this.devices.find(d => d.name === name));
        
        return name;
    }

    /**
     * Generate ports for device based on type
     */
    generatePortsForDevice(type) {
        const portConfigs = {
            router: { count: 4, prefix: 'GigabitEthernet0/', type: 'ethernet' },
            switch: { count: 24, prefix: 'FastEthernet0/', type: 'ethernet' },
            server: { count: 2, prefix: 'eth', type: 'ethernet' },
            wireless: { count: 1, prefix: 'wlan', type: 'wireless' },
            firewall: { count: 4, prefix: 'Port', type: 'ethernet' }
        };

        const config = portConfigs[type] || { count: 2, prefix: 'Port', type: 'ethernet' };
        const ports = [];

        for (let i = 0; i < config.count; i++) {
            ports.push({
                id: `${Date.now()}-${i}`,
                name: `${config.prefix}${i + 1}`,
                type: config.type,
                connected: false,
                connectedTo: null
            });
        }

        return ports;
    }

    /**
     * Handle canvas click events
     */
    handleCanvasClick(e) {
        const clickedElement = e.target.closest('.network-device');
        
        if (clickedElement) {
            const deviceId = parseInt(clickedElement.getAttribute('data-device-id'));
            const device = this.devices.find(d => d.id === deviceId);
            if (device) {
                this.handleDeviceClick(device, e);
            }
        } else {
            // Clicked on empty canvas
            this.handleEmptyCanvasClick(e);
        }
    }

    /**
     * Handle device click
     */
    handleDeviceClick(device, e) {
        e.stopPropagation();

        if (this.currentTool === 'select') {
            this.selectDevice(device);
        } else if (this.currentTool === 'connect') {
            this.handleConnectionTool(device);
        }
    }

    /**
     * Handle empty canvas click
     */
    handleEmptyCanvasClick(e) {
        if (this.currentTool === 'select') {
            this.deselectAll();
        }
    }

    /**
     * Handle canvas right-click for context menu
     */
    handleCanvasRightClick(e) {
        e.preventDefault();
        
        const clickedElement = e.target.closest('.network-device');
        if (clickedElement) {
            const deviceId = parseInt(clickedElement.getAttribute('data-device-id'));
            const device = this.devices.find(d => d.id === deviceId);
            if (device) {
                this.showDeviceContextMenu(device, e.clientX, e.clientY);
            }
        } else {
            this.showCanvasContextMenu(e.clientX, e.clientY);
        }
    }

    /**
     * Handle keyboard shortcuts
     */
    handleKeyDown(e) {
        // Only handle shortcuts when topology page is active
        if (!$('#topologyPage') || $('#topologyPage').classList.contains('hidden')) {
            return;
        }

        switch (e.key) {
            case 'Delete':
            case 'Backspace':
                if (this.selectedDevice) {
                    this.removeDevice(this.selectedDevice.id);
                } else if (this.selectedConnection) {
                    this.removeConnection(this.selectedConnection.id);
                }
                break;
            case 'Escape':
                this.deselectAll();
                this.setTool('select');
                break;
            case 'c':
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    this.copySelected();
                }
                break;
            case 'v':
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    this.pasteSelected();
                }
                break;
            case 'z':
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    if (e.shiftKey) {
                        this.redo();
                    } else {
                        this.undo();
                    }
                }
                break;
            case 'a':
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    this.selectAll();
                }
                break;
        }
    }

    /**
     * Set current tool
     */
    setTool(tool) {
        this.currentTool = tool;
        this.connectionStart = null;

        // Update tool buttons
        $$('.tool-btn').forEach(btn => btn.classList.remove('active'));
        $(`#${tool}Tool`)?.classList.add('active');

        // Update canvas cursor and status
        this.updateCanvasCursor();
        this.updateCanvasStatus(this.getToolStatusMessage(tool));
    }

    /**
     * Get status message for tool
     */
    getToolStatusMessage(tool) {
        const messages = {
            select: 'Click devices to select them',
            connect: 'Click two devices to connect them'
        };
        return messages[tool] || 'Tool selected';
    }

    /**
     * Update canvas cursor based on current tool
     */
    updateCanvasCursor() {
        const cursors = {
            select: 'default',
            connect: 'crosshair'
        };
        this.canvas.style.cursor = cursors[this.currentTool] || 'default';
    }

    /**
     * Select device
     */
    selectDevice(device) {
        this.selectedDevice = device;
        this.selectedConnection = null;
        this.updatePropertiesPanel();
        this.render();
    }

    /**
     * Deselect all items
     */
    deselectAll() {
        this.selectedDevice = null;
        this.selectedConnection = null;
        this.updatePropertiesPanel();
        this.render();
    }

    /**
     * Select all devices
     */
    selectAll() {
        // For simplicity, just select the first device
        if (this.devices.length > 0) {
            this.selectDevice(this.devices[0]);
        }
    }

    /**
     * Handle connection tool
     */
    handleConnectionTool(device) {
        if (!this.connectionStart) {
            this.connectionStart = device;
            this.updateCanvasStatus(`Click another device to connect to ${device.name}`);
            
            // Visual feedback
            this.render();
        } else if (this.connectionStart.id !== device.id) {
            this.createConnection(this.connectionStart, device);
            this.connectionStart = null;
            this.updateCanvasStatus('Connection created! Click devices to connect them');
        } else {
            // Clicked the same device, cancel connection
            this.connectionStart = null;
            this.updateCanvasStatus('Connection cancelled. Click devices to connect them');
            this.render();
        }
    }

    /**
     * Create connection between two devices
     */
    createConnection(device1, device2) {
        // Check if connection already exists
        const exists = this.connections.some(conn => 
            (conn.from === device1.id && conn.to === device2.id) ||
            (conn.from === device2.id && conn.to === device1.id)
        );

        if (exists) {
            showToast('Connection already exists between these devices', 'warning');
            return;
        }

        // Find available ports
        const fromPort = device1.ports.find(p => !p.connected);
        const toPort = device2.ports.find(p => !p.connected);

        if (!fromPort || !toPort) {
            showToast('No available ports on one or both devices', 'warning');
            return;
        }

        const connection = {
            id: Date.now(),
            from: device1.id,
            to: device2.id,
            fromPort: fromPort.id,
            toPort: toPort.id
        };

        // Mark ports as connected
        fromPort.connected = true;
        fromPort.connectedTo = toPort.id;
        toPort.connected = true;
        toPort.connectedTo = fromPort.id;

        this.connections.push(connection);
        this.render();
        this.saveState();
        showToast(`Connected ${device1.name} to ${device2.name}`, 'success');
    }

    /**
     * Remove connection
     */
    removeConnection(connectionId) {
        const connection = this.connections.find(c => c.id === connectionId);
        if (!connection) return;

        // Free up ports
        const fromDevice = this.devices.find(d => d.id === connection.from);
        const toDevice = this.devices.find(d => d.id === connection.to);

        if (fromDevice && toDevice) {
            const fromPort = fromDevice.ports.find(p => p.id === connection.fromPort);
            const toPort = toDevice.ports.find(p => p.id === connection.toPort);

            if (fromPort) {
                fromPort.connected = false;
                fromPort.connectedTo = null;
            }
            if (toPort) {
                toPort.connected = false;
                toPort.connectedTo = null;
            }
        }

        this.connections = this.connections.filter(c => c.id !== connectionId);
        this.selectedConnection = null;
        this.render();
        this.saveState();
        showToast('Connection removed', 'success');
    }

    /**
     * Remove device and its connections
     */
    removeDevice(deviceId) {
        const device = this.devices.find(d => d.id === deviceId);
        if (!device) return;

        if (!confirm(`Remove ${device.name} and all its connections?`)) {
            return;
        }

        // Remove related connections
        const connectionsToRemove = this.connections.filter(c => 
            c.from === deviceId || c.to === deviceId
        );
        
        connectionsToRemove.forEach(connection => {
            this.removeConnection(connection.id);
        });

        // Remove device
        this.devices = this.devices.filter(d => d.id !== deviceId);

        // Clear selection if removed device was selected
        if (this.selectedDevice?.id === deviceId) {
            this.selectedDevice = null;
            this.updatePropertiesPanel();
        }

        this.render();
        this.saveState();
        showToast(`${device.name} removed from topology`, 'success');
    }

    /**
     * Clear entire canvas
     */
    clearCanvas() {
        if (this.devices.length === 0 && this.connections.length === 0) {
            showToast('Canvas is already empty', 'info');
            return;
        }

        if (!confirm('Clear the entire topology? This cannot be undone.')) {
            return;
        }

        this.devices = [];
        this.connections = [];
        this.selectedDevice = null;
        this.selectedConnection = null;
        this.connectionStart = null;
        this.deviceCounter = 1;

        this.updatePropertiesPanel();
        this.render();
        this.saveState();
        this.updateCanvasStatus('Canvas cleared. Drag devices from the library to get started');
        showToast('Topology cleared', 'success');
    }

    /**
     * Render the entire topology
     */
    render() {
        if (!this.canvas) return;

        this.canvas.innerHTML = '';

        // Render connections first (so they appear behind devices)
        this.connections.forEach(connection => {
            this.renderConnection(connection);
        });

        // Render devices
        this.devices.forEach(device => {
            this.renderDevice(device);
        });

        // Render connection preview if in connect mode
        if (this.currentTool === 'connect' && this.connectionStart) {
            this.renderConnectionPreview();
        }
    }

    /**
     * Render a device on the canvas
     */
    renderDevice(device) {
        const deviceEl = createElement('div', 'network-device');
        deviceEl.style.left = device.x + 'px';
        deviceEl.style.top = device.y + 'px';
        deviceEl.setAttribute('data-device-id', device.id);
        deviceEl.setAttribute('data-device-type', device.type);

        // Apply selection state
        if (this.selectedDevice?.id === device.id) {
            deviceEl.classList.add('selected');
        }

        // Apply connection start state
        if (this.connectionStart?.id === device.id) {
            deviceEl.classList.add('connection-start');
        }

        deviceEl.innerHTML = `
            <div class="device-icon">
                <i class="${getDeviceIcon(device.type)}"></i>
            </div>
            <div class="device-label">${device.name}</div>
        `;

        // Make device draggable
        this.makeDeviceDraggable(deviceEl, device);

        this.canvas.appendChild(deviceEl);
    }

    /**
     * Make device draggable
     */
    makeDeviceDraggable(element, device) {
        let isDragging = false;
        let startX, startY, offsetX, offsetY;

        element.addEventListener('mousedown', (e) => {
            if (this.currentTool !== 'select') return;
            
            isDragging = true;
            this.draggedDevice = device;
            
            const rect = this.canvas.getBoundingClientRect();
            startX = e.clientX;
            startY = e.clientY;
            offsetX = e.clientX - rect.left - device.x;
            offsetY = e.clientY - rect.top - device.y;
            
            element.style.zIndex = '1000';
            element.classList.add('dragging');
            
            e.preventDefault();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging || this.draggedDevice !== device) return;

            const rect = this.canvas.getBoundingClientRect();
            let newX = e.clientX - rect.left - offsetX;
            let newY = e.clientY - rect.top - offsetY;

            // Snap to grid if enabled
            if (this.snapToGrid) {
                newX = Math.round(newX / this.gridSize) * this.gridSize;
                newY = Math.round(newY / this.gridSize) * this.gridSize;
            }

            // Keep device within canvas bounds
            newX = Math.max(0, Math.min(newX, rect.width - 80));
            newY = Math.max(0, Math.min(newY, rect.height - 80));

            device.x = newX;
            device.y = newY;

            element.style.left = newX + 'px';
            element.style.top = newY + 'px';

            // Update connections in real-time
            this.updateConnectionsForDevice(device.id);
        });

        document.addEventListener('mouseup', (e) => {
            if (isDragging && this.draggedDevice === device) {
                isDragging = false;
                this.draggedDevice = null;
                
                element.style.zIndex = '';
                element.classList.remove('dragging');
                
                // Save state after drag
                this.saveState();
            }
        });
    }

    /**
     * Render a connection line
     */
    renderConnection(connection) {
        const device1 = this.devices.find(d => d.id === connection.from);
        const device2 = this.devices.find(d => d.id === connection.to);

        if (!device1 || !device2) return;

        const line = createElement('div', 'connection-line');
        line.setAttribute('data-connection-id', connection.id);

        if (this.selectedConnection?.id === connection.id) {
            line.classList.add('selected');
        }

        this.updateConnectionPosition(line, device1, device2);

        line.addEventListener('click', (e) => {
            e.stopPropagation();
            this.selectedConnection = connection;
            this.selectedDevice = null;
            this.render();
        });

        this.canvas.appendChild(line);

        // Add connection points
        this.renderConnectionPoints(device1, device2);
    }

    /**
     * Update connection line position
     */
    updateConnectionPosition(line, device1, device2) {
        const x1 = device1.x + 40; // Center of device
        const y1 = device1.y + 40;
        const x2 = device2.x + 40;
        const y2 = device2.y + 40;

        const length = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
        const angle = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI;

        line.style.left = x1 + 'px';
        line.style.top = y1 + 'px';
        line.style.width = length + 'px';
        line.style.transform = `rotate(${angle}deg)`;
    }

    /**
     * Render connection points
     */
    renderConnectionPoints(device1, device2) {
        const x1 = device1.x + 40;
        const y1 = device1.y + 40;
        const x2 = device2.x + 40;
        const y2 = device2.y + 40;

        // Start point
        const startPoint = createElement('div', 'connection-point start');
        startPoint.style.left = x1 + 'px';
        startPoint.style.top = y1 + 'px';
        this.canvas.appendChild(startPoint);

        // End point
        const endPoint = createElement('div', 'connection-point end');
        endPoint.style.left = x2 + 'px';
        endPoint.style.top = y2 + 'px';
        this.canvas.appendChild(endPoint);
    }

    /**
     * Render connection preview while connecting
     */
    renderConnectionPreview() {
        if (!this.connectionStart) return;

        const preview = createElement('div', 'connection-preview');
        preview.style.position = 'absolute';
        preview.style.pointerEvents = 'none';
        preview.style.border = '2px dashed var(--primary-color)';
        preview.style.borderRadius = '20px';
        preview.style.background = 'rgba(37, 99, 235, 0.1)';

        const x = this.connectionStart.x - 10;
        const y = this.connectionStart.y - 10;
        const width = 100;
        const height = 100;

        preview.style.left = x + 'px';
        preview.style.top = y + 'px';
        preview.style.width = width + 'px';
        preview.style.height = height + 'px';

        this.canvas.appendChild(preview);
    }

    /**
     * Update connections for a specific device when it moves
     */
    updateConnectionsForDevice(deviceId) {
        this.connections.forEach(connection => {
            if (connection.from === deviceId || connection.to === deviceId) {
                const line = this.canvas.querySelector(`[data-connection-id="${connection.id}"]`);
                const device1 = this.devices.find(d => d.id === connection.from);
                const device2 = this.devices.find(d => d.id === connection.to);

                if (line && device1 && device2) {
                    this.updateConnectionPosition(line, device1, device2);
                }
            }
        });
    }

    /**
     * Update properties panel
     */
    updatePropertiesPanel() {
        const panel = $('#deviceProperties');
        if (!panel) return;

        if (this.selectedDevice) {
            const device = this.selectedDevice;
            const connectedPorts = device.ports.filter(p => p.connected).length;
            
            panel.innerHTML = `
                <div class="property-item">
                    <label class="property-label">Name</label>
                    <input type="text" class="property-input" value="${device.name}" 
                           onchange="topologyBuilder.updateDeviceName(${device.id}, this.value)">
                </div>
                <div class="property-item">
                    <label class="property-label">Type</label>
                    <div class="property-value">${device.type}</div>
                </div>
                <div class="property-item">
                    <label class="property-label">Position</label>
                    <div class="property-value">X: ${Math.round(device.x)}, Y: ${Math.round(device.y)}</div>
                </div>
                <div class="property-item">
                    <label class="property-label">Ports</label>
                    <div class="property-value">${connectedPorts}/${device.ports.length} connected</div>
                </div>
                <div class="property-actions">
                    <button class="btn btn-outline btn-sm" onclick="topologyBuilder.duplicateDevice(${device.id})">
                        <i class="fas fa-copy"></i>
                        Duplicate
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="topologyBuilder.removeDevice(${device.id})">
                        <i class="fas fa-trash"></i>
                        Remove
                    </button>
                </div>
            `;
        } else if (this.selectedConnection) {
            const connection = this.selectedConnection;
            const fromDevice = this.devices.find(d => d.id === connection.from);
            const toDevice = this.devices.find(d => d.id === connection.to);
            
            panel.innerHTML = `
                <div class="property-item">
                    <label class="property-label">Connection</label>
                    <div class="property-value">${fromDevice?.name || 'Unknown'} ↔ ${toDevice?.name || 'Unknown'}</div>
                </div>
                <div class="property-item">
                    <label class="property-label">From Port</label>
                    <div class="property-value">${this.getPortName(fromDevice, connection.fromPort)}</div>
                </div>
                <div class="property-item">
                    <label class="property-label">To Port</label>
                    <div class="property-value">${this.getPortName(toDevice, connection.toPort)}</div>
                </div>
                <div class="property-actions">
                    <button class="btn btn-danger btn-sm" onclick="topologyBuilder.removeConnection(${connection.id})">
                        <i class="fas fa-unlink"></i>
                        Disconnect
                    </button>
                </div>
            `;
        } else {
            panel.innerHTML = `
                <p class="text-muted text-center">Select a device or connection to view properties</p>
                <div class="topology-stats">
                    <div class="stat-item">
                        <span class="stat-label">Devices</span>
                        <span class="stat-value">${this.devices.length}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Connections</span>
                        <span class="stat-value">${this.connections.length}</span>
                    </div>
                </div>
            `;
        }
    }

    /**
     * Get port name by ID
     */
    getPortName(device, portId) {
        if (!device) return 'Unknown';
        const port = device.ports.find(p => p.id === portId);
        return port ? port.name : 'Unknown';
    }

    /**
     * Update device name
     */
    updateDeviceName(deviceId, newName) {
        const device = this.devices.find(d => d.id === deviceId);
        if (device && newName.trim()) {
            device.name = newName.trim();
            this.render();
            this.saveState();
        }
    }

    /**
     * Duplicate device
     */
    duplicateDevice(deviceId) {
        const device = this.devices.find(d => d.id === deviceId);
        if (!device) return;

        const newDevice = {
            ...deepClone(device),
            id: Date.now(),
            name: this.generateDeviceName(device.type),
            x: device.x + 100,
            y: device.y + 50,
            ports: this.generatePortsForDevice(device.type)
        };

        this.devices.push(newDevice);
        this.render();
        this.saveState();
        showToast(`${newDevice.name} created`, 'success');
    }

    /**
     * Update canvas status message
     */
    updateCanvasStatus(message) {
        const statusEl = $('#canvasStatus');
        if (statusEl) {
            statusEl.textContent = message;
        }
    }

    /**
     * Update canvas rect for coordinate calculations
     */
    updateCanvasRect() {
        if (this.canvas) {
            this.canvasRect = this.canvas.getBoundingClientRect();
        }
    }

    /**
     * Show device context menu
     */
    showDeviceContextMenu(device, x, y) {
        const contextMenu = createElement('div', 'context-menu');
        contextMenu.style.position = 'fixed';
        contextMenu.style.left = x + 'px';
        contextMenu.style.top = y + 'px';
        contextMenu.style.zIndex = '9999';

        contextMenu.innerHTML = `
            <div class="context-menu-item" onclick="topologyBuilder.editDevice(${device.id})">
                <i class="fas fa-edit"></i>
                Edit Properties
            </div>
            <div class="context-menu-item" onclick="topologyBuilder.duplicateDevice(${device.id})">
                <i class="fas fa-copy"></i>
                Duplicate
            </div>
            <div class="context-menu-divider"></div>
            <div class="context-menu-item danger" onclick="topologyBuilder.removeDevice(${device.id})">
                <i class="fas fa-trash"></i>
                Remove Device
            </div>
        `;

        document.body.appendChild(contextMenu);

        // Remove context menu on click outside
        setTimeout(() => {
            document.addEventListener('click', () => {
                contextMenu.remove();
            }, { once: true });
        }, 0);
    }

    /**
     * Show canvas context menu
     */
    showCanvasContextMenu(x, y) {
        const contextMenu = createElement('div', 'context-menu');
        contextMenu.style.position = 'fixed';
        contextMenu.style.left = x + 'px';
        contextMenu.style.top = y + 'px';
        contextMenu.style.zIndex = '9999';

        contextMenu.innerHTML = `
            <div class="context-menu-item" onclick="topologyBuilder.selectAll()">
                <i class="fas fa-check-square"></i>
                Select All
            </div>
            <div class="context-menu-item" onclick="topologyBuilder.pasteSelected()">
                <i class="fas fa-paste"></i>
                Paste
            </div>
            <div class="context-menu-divider"></div>
            <div class="context-menu-item" onclick="topologyBuilder.clearCanvas()">
                <i class="fas fa-trash"></i>
                Clear Canvas
            </div>
        `;

        document.body.appendChild(contextMenu);

        // Remove context menu on click outside
        setTimeout(() => {
            document.addEventListener('click', () => {
                contextMenu.remove();
            }, { once: true });
        }, 0);
    }

    /**
     * Copy selected device
     */
    copySelected() {
        if (this.selectedDevice) {
            const deviceData = deepClone(this.selectedDevice);
            setLocalStorage('copiedDevice', deviceData);
            showToast('Device copied', 'success');
        }
    }

    /**
     * Paste copied device
     */
    pasteSelected() {
        const copiedDevice = getLocalStorage('copiedDevice');
        if (!copiedDevice) {
            showToast('Nothing to paste', 'warning');
            return;
        }

        const newDevice = {
            ...copiedDevice,
            id: Date.now(),
            name: this.generateDeviceName(copiedDevice.type),
            x: copiedDevice.x + 50,
            y: copiedDevice.y + 50,
            ports: this.generatePortsForDevice(copiedDevice.type)
        };

        this.devices.push(newDevice);
        this.render();
        this.saveState();
        showToast(`${newDevice.name} pasted`, 'success');
    }

    /**
     * Undo last action
     */
    undo() {
        if (this.historyIndex > 0) {
            this.historyIndex--;
            this.loadState(this.history[this.historyIndex]);
            showToast('Undone', 'info');
        }
    }

    /**
     * Redo last undone action
     */
    redo() {
        if (this.historyIndex < this.history.length - 1) {
            this.historyIndex++;
            this.loadState(this.history[this.historyIndex]);
            showToast('Redone', 'info');
        }
    }

    /**
     * Save current state to history
     */
    saveState() {
        const state = {
            devices: deepClone(this.devices),
            connections: deepClone(this.connections)
        };

        // Remove future states if we're not at the end
        if (this.historyIndex < this.history.length - 1) {
            this.history = this.history.slice(0, this.historyIndex + 1);
        }

        this.history.push(state);

        // Limit history size
        if (this.history.length > this.maxHistory) {
            this.history.shift();
        } else {
            this.historyIndex++;
        }
    }

    /**
     * Load state from history
     */
    loadState(state) {
        this.devices = deepClone(state.devices);
        this.connections = deepClone(state.connections);
        this.selectedDevice = null;
        this.selectedConnection = null;
        this.connectionStart = null;
        this.updatePropertiesPanel();
        this.render();
    }

    /**
     * Load topology from storage or API
     */
    async loadTopology() {
        try {
            // Try to load from API first
            const topology = await api.getTopology();
            if (topology.devices && topology.connections) {
                this.devices = topology.devices;
                this.connections = topology.connections;
                this.render();
                console.log('Topology loaded from API');
                return;
            }
        } catch (error) {
            console.log('No topology found in API, starting with empty canvas');
        }

        // Load from localStorage as fallback
        const savedTopology = getLocalStorage('topology');
        if (savedTopology) {
            this.devices = savedTopology.devices || [];
            this.connections = savedTopology.connections || [];
            this.render();
            console.log('Topology loaded from localStorage');
        }
    }

    /**
     * Save topology to storage and API
     */
    async saveTopology() {
        const topology = {
            devices: this.devices,
            connections: this.connections,
            metadata: {
                version: '1.0',
                created: new Date().toISOString(),
                deviceCount: this.devices.length,
                connectionCount: this.connections.length
            }
        };

        try {
            // Save to localStorage
            setLocalStorage('topology', topology);

            // Save to API
            await api.saveTopology(topology);
            
            showToast('Topology saved successfully', 'success');
            console.log('Topology saved');
        } catch (error) {
            console.error('Failed to save topology:', error);
            showToast('Failed to save topology: ' + error.message, 'error');
        }
    }

    /**
     * Export topology as JSON file
     */
    exportTopology() {
        const topology = {
            devices: this.devices,
            connections: this.connections,
            metadata: {
                version: '1.0',
                exported: new Date().toISOString(),
                deviceCount: this.devices.length,
                connectionCount: this.connections.length
            }
        };

        downloadJSON(topology, `network-topology-${formatDate(new Date())}.json`);
        showToast('Topology exported', 'success');
    }

    /**
     * Import topology from JSON file
     */
    importTopologyDialog() {
        const input = createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.importTopology(file);
            }
        });
        input.click();
    }

    /**
     * Import topology from file
     */
    importTopology(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const topology = JSON.parse(e.target.result);
                
                if (!topology.devices || !topology.connections) {
                    throw new Error('Invalid topology file format');
                }

                if (this.devices.length > 0 || this.connections.length > 0) {
                    if (!confirm('This will replace the current topology. Continue?')) {
                        return;
                    }
                }

                this.devices = topology.devices;
                this.connections = topology.connections;
                this.selectedDevice = null;
                this.selectedConnection = null;
                this.connectionStart = null;

                this.updatePropertiesPanel();
                this.render();
                this.saveState();
                
                showToast('Topology imported successfully', 'success');
                console.log('Topology imported:', topology.metadata);
                
            } catch (error) {
                console.error('Failed to import topology:', error);
                showToast('Failed to import topology: Invalid file format', 'error');
            }
        };
        reader.readAsText(file);
    }

    /**
     * Zoom controls
     */
    zoomIn() {
        // Placeholder for zoom functionality
        showToast('Zoom in functionality coming soon', 'info');
    }

    zoomOut() {
        // Placeholder for zoom functionality
        showToast('Zoom out functionality coming soon', 'info');
    }

    resetZoom() {
        // Placeholder for zoom functionality
        showToast('Zoom reset functionality coming soon', 'info');
    }

    /**
     * Auto-layout algorithms
     */
    autoLayout(algorithm = 'grid') {
        if (this.devices.length === 0) {
            showToast('No devices to layout', 'warning');
            return;
        }

        switch (algorithm) {
            case 'grid':
                this.gridLayout();
                break;
            case 'circle':
                this.circleLayout();
                break;
            case 'force':
                this.forceLayout();
                break;
            default:
                this.gridLayout();
        }

        this.render();
        this.saveState();
        showToast('Auto-layout applied', 'success');
    }

    /**
     * Grid layout algorithm
     */
    gridLayout() {
        const cols = Math.ceil(Math.sqrt(this.devices.length));
        const spacing = 150;
        const startX = 50;
        const startY = 50;

        this.devices.forEach((device, index) => {
            const row = Math.floor(index / cols);
            const col = index % cols;
            device.x = startX + col * spacing;
            device.y = startY + row * spacing;
        });
    }

    /**
     * Circle layout algorithm
     */
    circleLayout() {
        const centerX = 300;
        const centerY = 200;
        const radius = 150;
        const angleStep = (2 * Math.PI) / this.devices.length;

        this.devices.forEach((device, index) => {
            const angle = index * angleStep;
            device.x = centerX + radius * Math.cos(angle) - 40;
            device.y = centerY + radius * Math.sin(angle) - 40;
        });
    }

    /**
     * Force-directed layout algorithm (simplified)
     */
    forceLayout() {
        // Simple force-directed layout
        const iterations = 50;
        const repulsion = 5000;
        const attraction = 0.1;

        for (let i = 0; i < iterations; i++) {
            // Calculate repulsive forces
            this.devices.forEach(device1 => {
                let fx = 0, fy = 0;

                this.devices.forEach(device2 => {
                    if (device1.id !== device2.id) {
                        const dx = device1.x - device2.x;
                        const dy = device1.y - device2.y;
                        const distance = Math.sqrt(dx * dx + dy * dy) || 1;
                        const force = repulsion / (distance * distance);
                        fx += (dx / distance) * force;
                        fy += (dy / distance) * force;
                    }
                });

                // Calculate attractive forces for connected devices
                this.connections.forEach(connection => {
                    if (connection.from === device1.id || connection.to === device1.id) {
                        const otherId = connection.from === device1.id ? connection.to : connection.from;
                        const other = this.devices.find(d => d.id === otherId);
                        if (other) {
                            const dx = other.x - device1.x;
                            const dy = other.y - device1.y;
                            fx += dx * attraction;
                            fy += dy * attraction;
                        }
                    }
                });

                // Apply forces
                device1.x += fx * 0.01;
                device1.y += fy * 0.01;

                // Keep within bounds
                device1.x = Math.max(0, Math.min(device1.x, 600));
                device1.y = Math.max(0, Math.min(device1.y, 400));
            });
        }
    }

    /**
     * Get topology data for export
     */
    getTopologyData() {
        return {
            devices: this.devices,
            connections: this.connections,
            metadata: {
                version: '1.0',
                created: new Date().toISOString(),
                deviceCount: this.devices.length,
                connectionCount: this.connections.length
            }
        };
    }

    /**
     * Get topology statistics
     */
    getTopologyStats() {
        return {
            deviceCount: this.devices.length,
            connectionCount: this.connections.length,
            deviceTypes: groupBy(this.devices, 'type'),
            connectedDevices: this.devices.filter(d => 
                d.ports.some(p => p.connected)
            ).length,
            isolatedDevices: this.devices.filter(d => 
                !d.ports.some(p => p.connected)
            ).length
        };
    }

    /**
     * Validate topology
     */
    validateTopology() {
        const issues = [];

        // Check for isolated devices
        const isolatedDevices = this.devices.filter(d => 
            !d.ports.some(p => p.connected)
        );
        if (isolatedDevices.length > 0) {
            issues.push(`${isolatedDevices.length} isolated device(s)`);
        }

        // Check for devices with no available ports
        const fullDevices = this.devices.filter(d => 
            d.ports.every(p => p.connected)
        );
        if (fullDevices.length > 0) {
            issues.push(`${fullDevices.length} device(s) with no available ports`);
        }

        return {
            isValid: issues.length === 0,
            issues: issues
        };
    }

    /**
     * Cleanup resources
     */
    destroy() {
        this.devices = [];
        this.connections = [];
        this.selectedDevice = null;
        this.selectedConnection = null;
        this.connectionStart = null;
        this.history = [];
        this.historyIndex = -1;
        this.isInitialized = false;
        
        console.log('Topology builder destroyed');
    }
}

// Create global topology builder instance
const topologyBuilder = new TopologyBuilder();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { TopologyBuilder, topologyBuilder };
}

console.log('Topology builder loaded');