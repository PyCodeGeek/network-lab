# # docker/backend.Dockerfile
# FROM python:3.9-slim

# WORKDIR /app

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     gcc \
#     libpq-dev \
#     && rm -rf /var/lib/apt/lists/*

# # Copy requirements and install Python dependencies
# COPY backend/requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy application code
# COPY backend/ .

# # Expose port
# EXPOSE 5000

# # Run the application
# CMD ["python", "run.py"]

# ---
# # backend/requirements.txt
# Flask==2.3.3
# Flask-SQLAlchemy==3.0.5
# Flask-Migrate==4.0.5
# Flask-CORS==4.0.0
# Flask-JWT-Extended==4.5.3
# psycopg2-binary==2.9.7
# redis==4.6.0
# celery==5.3.1
# paramiko==3.3.1
# netmiko==4.2.0
# jinja2==3.1.2
# requests==2.31.0
# python-dotenv==1.0.0
# gunicorn==21.2.0

# ---
# # db/init.sql
# -- Network Lab Automation Database Schema

# -- Create database (this is handled by Docker, but included for reference)
# -- CREATE DATABASE network_lab;

# -- Users table
# CREATE TABLE IF NOT EXISTS users (
#     id SERIAL PRIMARY KEY,
#     username VARCHAR(64) UNIQUE NOT NULL,
#     email VARCHAR(120) UNIQUE NOT NULL,
#     password_hash VARCHAR(256) NOT NULL,
#     role VARCHAR(20) DEFAULT 'user',
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Devices table
# CREATE TABLE IF NOT EXISTS devices (
#     id SERIAL PRIMARY KEY,
#     name VARCHAR(100) NOT NULL,
#     device_type VARCHAR(50) NOT NULL,
#     ip_address VARCHAR(15) NOT NULL,
#     username VARCHAR(50),
#     password VARCHAR(100),
#     ssh_port INTEGER DEFAULT 22,
#     status VARCHAR(20) DEFAULT 'inactive',
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Ports table
# CREATE TABLE IF NOT EXISTS ports (
#     id SERIAL PRIMARY KEY,
#     device_id INTEGER REFERENCES devices(id) ON DELETE CASCADE,
#     name VARCHAR(50) NOT NULL,
#     port_type VARCHAR(20) NOT NULL,
#     status VARCHAR(20) DEFAULT 'down',
#     connected_to_port_id INTEGER REFERENCES ports(id),
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Inventory table
# CREATE TABLE IF NOT EXISTS inventory (
#     id SERIAL PRIMARY KEY,
#     device_id INTEGER REFERENCES devices(id) ON DELETE CASCADE,
#     hardware_model VARCHAR(100),
#     serial_number VARCHAR(100) UNIQUE,
#     os_version VARCHAR(50),
#     last_inventory_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Interface inventory table
# CREATE TABLE IF NOT EXISTS interface_inventory (
#     id SERIAL PRIMARY KEY,
#     inventory_id INTEGER REFERENCES inventory(id) ON DELETE CASCADE,
#     port_id INTEGER REFERENCES ports(id) ON DELETE CASCADE,
#     mac_address VARCHAR(17),
#     speed VARCHAR(20),
#     duplex VARCHAR(10),
#     mtu INTEGER
# );

# -- Configuration templates table
# CREATE TABLE IF NOT EXISTS config_templates (
#     id SERIAL PRIMARY KEY,
#     name VARCHAR(100) NOT NULL,
#     device_type VARCHAR(50) NOT NULL,
#     content TEXT NOT NULL,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Provisioning tasks table
# CREATE TABLE IF NOT EXISTS provisioning_tasks (
#     id SERIAL PRIMARY KEY,
#     device_id INTEGER REFERENCES devices(id) ON DELETE CASCADE,
#     template_id INTEGER REFERENCES config_templates(id),
#     status VARCHAR(20) DEFAULT 'pending',
#     config_data TEXT,
#     result TEXT,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     completed_at TIMESTAMP
# );

# -- Telemetry configuration table
# CREATE TABLE IF NOT EXISTS telemetry_configs (
#     id SERIAL PRIMARY KEY,
#     device_id INTEGER REFERENCES devices(id) ON DELETE CASCADE,
#     metrics TEXT,
#     collection_interval INTEGER DEFAULT 60,
#     enabled BOOLEAN DEFAULT TRUE,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Telemetry data table
# CREATE TABLE IF NOT EXISTS telemetry_data (
#     id SERIAL PRIMARY KEY,
#     device_id INTEGER REFERENCES devices(id) ON DELETE CASCADE,
#     metric VARCHAR(100) NOT NULL,
#     value FLOAT,
#     unit VARCHAR(20),
#     timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Reports table
# CREATE TABLE IF NOT EXISTS reports (
#     id SERIAL PRIMARY KEY,
#     name VARCHAR(100) NOT NULL,
#     report_type VARCHAR(50) NOT NULL,
#     parameters TEXT,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     generated_at TIMESTAMP,
#     status VARCHAR(20) DEFAULT 'pending',
#     result TEXT
# );

# -- Topology table for storing network topology
# CREATE TABLE IF NOT EXISTS topology_devices (
#     id SERIAL PRIMARY KEY,
#     device_id INTEGER REFERENCES devices(id) ON DELETE CASCADE,
#     x_position FLOAT NOT NULL,
#     y_position FLOAT NOT NULL,
#     topology_name VARCHAR(100) DEFAULT 'default',
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Topology connections table
# CREATE TABLE IF NOT EXISTS topology_connections (
#     id SERIAL PRIMARY KEY,
#     from_device_id INTEGER REFERENCES devices(id) ON DELETE CASCADE,
#     to_device_id INTEGER REFERENCES devices(id) ON DELETE CASCADE,
#     from_port_id INTEGER REFERENCES ports(id),
#     to_port_id INTEGER REFERENCES ports(id),
#     topology_name VARCHAR(100) DEFAULT 'default',
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Create indexes for better performance
# CREATE INDEX IF NOT EXISTS idx_devices_type ON devices(device_type);
# CREATE INDEX IF NOT EXISTS idx_devices_status ON devices(status);
# CREATE INDEX IF NOT EXISTS idx_telemetry_device_timestamp ON telemetry_data(device_id, timestamp);
# CREATE INDEX IF NOT EXISTS idx_telemetry_metric ON telemetry_data(metric);
# CREATE INDEX IF NOT EXISTS idx_ports_device ON ports(device_id);
# CREATE INDEX IF NOT EXISTS idx_provisioning_tasks_device ON provisioning_tasks(device_id);
# CREATE INDEX IF NOT EXISTS idx_provisioning_tasks_status ON provisioning_tasks(status);

# -- Insert default admin user (password: admin123)
# INSERT INTO users (username, email, password_hash, role) 
# VALUES ('admin', 'admin@networklab.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewJFkPr1gEjOFTOq', 'admin')
# ON CONFLICT (username) DO NOTHING;

# -- Insert sample configuration templates
# INSERT INTO config_templates (name, device_type, content) VALUES
# ('Basic Router Config', 'router', 
# '! Basic Router Configuration Template
# !
# hostname {{ hostname }}
# !
# interface GigabitEthernet0/0
#  ip address {{ mgmt_ip }} {{ mgmt_mask }}
#  no shutdown
# !
# interface GigabitEthernet0/1
#  description {{ wan_description }}
#  ip address {{ wan_ip }} {{ wan_mask }}
#  no shutdown
# !
# router ospf 1
#  network {{ lan_network }} {{ lan_wildcard }} area 0
# !
# line vty 0 4
#  transport input ssh
#  login local
# !
# end'),

# ('Basic Switch Config', 'switch',
# '! Basic Switch Configuration Template
# !
# hostname {{ hostname }}
# !
# vlan {{ vlan_id }}
#  name {{ vlan_name }}
# !
# interface range GigabitEthernet1/0/1-24
#  switchport mode access
#  switchport access vlan {{ vlan_id }}
# !
# interface GigabitEthernet1/0/1
#  description {{ uplink_description }}
#  switchport mode trunk
# !
# spanning-tree mode rapid-pvst
# !
# end')
# ON CONFLICT DO NOTHING;

# -- Insert sample devices
# INSERT INTO devices (name, device_type, ip_address, username, status) VALUES
# ('Core-Router-01', 'router', '192.168.1.1', 'admin', 'active'),
# ('Access-Switch-01', 'switch', '192.168.1.2', 'admin', 'active'),
# ('Distribution-Switch-01', 'switch', '192.168.1.3', 'admin', 'inactive'),
# ('Wireless-AP-01', 'wireless', '192.168.1.50', 'admin', 'active'),
# ('Firewall-01', 'firewall', '192.168.1.254', 'admin', 'active')
# ON CONFLICT DO NOTHING;

# ---
# # .env.example
# # Flask Configuration
# FLASK_ENV=development
# FLASK_DEBUG=True
# SECRET_KEY=your-secret-key-here
# JWT_SECRET_KEY=your-jwt-secret-key-here

# # Database Configuration
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/network_lab
# POSTGRES_DB=network_lab
# POSTGRES_USER=postgres
# POSTGRES_PASSWORD=postgres

# # Redis Configuration
# REDIS_URL=redis://localhost:6379/0

# # Network Device Credentials (for automated provisioning)
# DEFAULT_DEVICE_USERNAME=admin
# DEFAULT_DEVICE_PASSWORD=admin

# # Email Configuration (for notifications)
# MAIL_SERVER=smtp.gmail.com
# MAIL_PORT=587
# MAIL_USE_TLS=True
# MAIL_USERNAME=your-email@gmail.com
# MAIL_PASSWORD=your-app-password

# # Celery Configuration
# CELERY_BROKER_URL=redis://localhost:6379/0
# CELERY_RESULT_BACKEND=redis://localhost:6379/0

# ---
# # README.md
# # Network Lab Automation Framework

# A comprehensive network lab automation framework with an interactive web UI for managing network devices, building topologies, and automating network operations.

# ## Features

# ### Core Functionality
# - **Device Management**: Add, configure, and manage network devices (routers, switches, servers, wireless APs, firewalls)
# - **Interactive Topology Builder**: Drag-and-drop interface for building network topologies (similar to GNS3)
# - **Inventory Management**: Automated device discovery and inventory tracking
# - **Device Provisioning**: Template-based configuration deployment
# - **Telemetry Collection**: Real-time monitoring and data collection
# - **Report Generation**: Automated report generation for various network metrics

# ### Web Interface
# - **Professional UI**: Modern, responsive web interface built with HTML5, CSS3, and JavaScript
# - **Real-time Dashboard**: Live network status and performance metrics
# - **Drag-and-Drop Topology**: Visual network topology builder with device connections
# - **Device Properties**: Interactive device configuration and management
# - **User Authentication**: Secure login system with role-based access

# ### Backend Services
# - **RESTful API**: Flask-based API server with comprehensive endpoints
# - **PostgreSQL Database**: Robust data storage for devices, configurations, and telemetry
# - **Authentication**: JWT-based authentication system
# - **Background Tasks**: Celery-based task queue for long-running operations

# ## Quick Start

# ### Prerequisites
# - Docker and Docker Compose
# - Python 3.9+ (for local development)
# - PostgreSQL 13+ (if running without Docker)
# - Redis (for background tasks)

# ### Using Docker (Recommended)

# 1. Clone the repository:
# ```bash
# git clone <repository-url>
# cd network_lab_automation
# ```

# 2. Copy environment configuration:
# ```bash
# cp .env.example .env
# # Edit .env with your configuration
# ```

# 3. Start the application:
# ```bash
# docker-compose up -d
# ```

# 4. Access the application:
# - Web Interface: http://localhost:3232
# - API Documentation: http://localhost:5000/api/docs
# - Database: localhost:5432

# 5. Default login credentials:
# - Username: `admin`
# - Password: `admin`

# ### Manual Installation

# 1. **Database Setup**:
# ```bash
# # Install PostgreSQL and create database
# createdb network_lab
# psql network_lab < db/init.sql
# ```

# 2. **Backend Setup**:
# ```bash
# cd backend
# pip install -r requirements.txt
# export FLASK_APP=run.py
# export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/network_lab
# flask run
# ```

# 3. **Frontend Setup**:
# ```bash
# # Serve the HTML file using any web server
# cd frontend
# python -m http.server 3232
# # Or use nginx, Apache, etc.
# ```

# ## Architecture

# ### Backend Structure
# ```
# backend/
# ├── app/
# │   ├── auth/          # Authentication module
# │   ├── devices/       # Device management
# │   ├── inventory/     # Network inventory
# │   ├── provisioning/  # Device provisioning
# │   ├── telemetry/     # Telemetry collection
# │   └── reports/       # Report generation
# ├── migrations/        # Database migrations
# └── run.py            # Application entry point
# ```

# ### Database Schema
# - **Users**: Authentication and user management
# - **Devices**: Network device information
# - **Ports**: Device port configuration
# - **Inventory**: Hardware inventory tracking
# - **Telemetry**: Performance metrics storage
# - **Reports**: Generated report metadata
# - **Topology**: Network topology storage

# ### API Endpoints

# #### Authentication
# - `POST /api/auth/login` - User login
# - `POST /api/auth/register` - User registration
# - `GET /api/auth/profile` - Get user profile

# #### Device Management
# - `GET /api/devices` - List all devices
# - `POST /api/devices` - Create new device
# - `GET /api/devices/{id}` - Get device details
# - `PUT /api/devices/{id}` - Update device
# - `DELETE /api/devices/{id}` - Delete device

# #### Inventory
# - `GET /api/inventory` - Get inventory data
# - `POST /api/inventory/{device_id}` - Update device inventory
# - `POST /api/inventory/scan/{device_id}` - Scan device inventory

# #### Provisioning
# - `GET /api/provisioning/templates` - List configuration templates
# - `POST /api/provisioning/templates` - Create template
# - `POST /api/provisioning/tasks` - Create provisioning task
# - `GET /api/provisioning/tasks` - List provisioning tasks

# #### Telemetry
# - `GET /api/telemetry/data/{device_id}` - Get telemetry data
# - `POST /api/telemetry/config/{device_id}` - Configure telemetry
# - `POST /api/telemetry/collect/{device_id}` - Collect telemetry

# #### Reports
# - `GET /api/reports` - List reports
# - `POST /api/reports` - Generate new report
# - `GET /api/reports/{id}/download` - Download report

# ## Features Deep Dive

# ### Topology Builder
# The interactive topology builder provides:
# - **Device Library**: Drag devices from a palette onto the canvas
# - **Visual Connections**: Click and drag to connect devices
# - **Device Properties**: Real-time property editing
# - **Connection Management**: Visual connection creation and deletion
# - **Canvas Tools**: Select, connect, and delete tools
# - **Responsive Design**: Works on desktop and tablet devices

# ### Device Provisioning
# Template-based configuration system supporting:
# - **Jinja2 Templates**: Dynamic configuration generation
# - **Device-Specific Templates**: Router, switch, and firewall templates
# - **Variable Substitution**: Runtime parameter injection
# - **Task Tracking**: Monitor provisioning progress
# - **Error Handling**: Detailed error reporting and rollback

# ### Telemetry Collection
# Real-time monitoring capabilities:
# - **Multi-Protocol Support**: SNMP, SSH, NETCONF
# - **Configurable Metrics**: CPU, memory, interface statistics
# - **Time-Series Storage**: Historical data retention
# - **Alerting**: Threshold-based notifications
# - **Visualization**: Charts and graphs for metrics

# ### Security
# - **JWT Authentication**: Secure token-based authentication
# - **Role-Based Access**: Admin and user roles
# - **Input Validation**: Comprehensive input sanitization
# - **HTTPS Support**: SSL/TLS encryption support
# - **Audit Logging**: Complete audit trail of operations

# ## Development

# ### Adding New Device Types
# 1. Update device type constants in `backend/app/devices/models.py`
# 2. Add device icons to the frontend device library
# 3. Create device-specific configuration templates
# 4. Update provisioning logic for new device type

# ### Adding New Telemetry Metrics
# 1. Add metric definition to `backend/app/telemetry/models.py`
# 2. Implement collection logic in `backend/app/telemetry/collector.py`
# 3. Update frontend visualization components

# ### Custom Report Types
# 1. Create report generator in `backend/app/reports/generator.py`
# 2. Add report type to the database
# 3. Update frontend report creation interface

# ## Deployment

# ### Production Deployment
# 1. **Environment Configuration**:
#    - Set production environment variables
#    - Configure SSL certificates
#    - Set up monitoring and logging

# 2. **Database Setup**:
#    - Use managed PostgreSQL service
#    - Configure connection pooling
#    - Set up regular backups

# 3. **Application Deployment**:
#    - Use production WSGI server (Gunicorn)
#    - Configure reverse proxy (Nginx)
#    - Set up load balancing if needed

# 4. **Monitoring**:
#    - Set up application monitoring
#    - Configure log aggregation
#    - Implement health checks

# ### Scaling Considerations
# - **Database**: Use read replicas for read-heavy workloads
# - **Background Tasks**: Scale Celery workers based on load
# - **Caching**: Implement Redis caching for frequently accessed data
# - **CDN**: Use CDN for static assets

# ## Contributing

# 1. Fork the repository
# 2. Create a feature branch
# 3. Make your changes
# 4. Add tests for new functionality
# 5. Submit a pull request

# ## License

# This project is licensed under the MIT License - see the LICENSE file for details.

# ## Support

# For support and questions:
# - Create an issue in the GitHub repository
# - Check the documentation wiki
# - Contact the development team

# ---

# **Network Lab Automation Framework** - Professional-grade network automation for modern infrastructure.# docker-compose.yml
# version: '3.8'

# services:
#   db:
#     image: postgres:13
#     container_name: network_lab_db
#     environment:
#       POSTGRES_DB: network_lab
#       POSTGRES_USER: postgres
#       POSTGRES_PASSWORD: postgres
#     ports:
#       - "5432:5432"
#     volumes:
#       - postgres_data:/var/lib/postgresql/data
#       - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql
#     healthcheck:
#       test: ["CMD-SHELL", "pg_isready -U postgres"]
#       interval: 30s
#       timeout: 10s
#       retries: 3

#   backend:
#     build:
#       context: .
#       dockerfile: docker/backend.Dockerfile
#     container_name: network_lab_backend
#     environment:
#       DATABASE_URL: postgresql://postgres:postgres@db:5432/network_lab
#       FLASK_ENV: development
#       SECRET_KEY: dev-secret-key-change-in-production
#       JWT_SECRET_KEY: jwt-secret-key-change-in-production
#     ports:
#       - "5000:5000"
#     depends_on:
#       db:
#         condition: service_healthy
#     volumes:
#       - ./backend:/app
#     command: python run.py

#   frontend:
#     build:
#       context: .
#       dockerfile: docker/frontend.Dockerfile
#     container_name: network_lab_frontend
#     ports:
#       - "3232:3232"
#     depends_on:
#       - backend
#     volumes:
#       - ./frontend:/app
#       - /app/node_modules
#     environment:
#       REACT_APP_API_URL: http://localhost:5000/api

#   redis:
#     image: redis:6-alpine
#     container_name: network_lab_redis
#     ports:
#       - "6379:6379"
#     command: redis-server --appendonly yes
#     volumes:
#       - redis_data:/data

# volumes:
#   postgres_data:
#   redis_data:

# ---
# # docker/backend.Dockerfile
# FROM python:3.9-slim

# WORKDIR /app

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     gcc \
#     libpq-dev \
#     && rm -rf /var/lib/apt/lists/*

# # Copy requirements and install Python dependencies
# COPY backend/requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy application code
# COPY backend/ .

# # Expose port
# EXPOSE 5000

# # Run the application
# CMD ["python", "run.py"]

# ---
# # docker/frontend.Dockerfile
# FROM node:16-alpine

# WORKDIR /app

# # Copy package files
# COPY frontend/package*.json ./

# # Install dependencies
# RUN npm ci --only=production

# # Copy source code
# COPY frontend/ .

# # Build the






# docker/backend.Dockerfile - Backend container
# =============================================

FROM python:3.8 as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY backend/requirements.txt ./
COPY backend/requirements-dev.txt ./

# Development stage
FROM base as development

# Install dev dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy application code
COPY backend/ ./

# Create logs directory
RUN mkdir -p logs && chown -R appuser:appuser logs

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Default command
CMD ["python", "run.py"]

# Production stage
FROM base as production

# Install only production dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install gunicorn for production
RUN pip install gunicorn==20.1.0

# Copy application code
COPY backend/ ./

# Create logs directory
RUN mkdir -p logs && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Production command
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "60", "run:app"]