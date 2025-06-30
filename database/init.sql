-- database/init.sql - Network Lab Automation Database Schema
-- PostgreSQL 13+ Compatible

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Drop existing tables if they exist (for clean reinstall)
DROP TABLE IF EXISTS telemetry_data CASCADE;
DROP TABLE IF EXISTS interface_inventory CASCADE;
DROP TABLE IF EXISTS inventory CASCADE;
DROP TABLE IF EXISTS topology_connections CASCADE;
DROP TABLE IF EXISTS topology_devices CASCADE;
DROP TABLE IF EXISTS provisioning_tasks CASCADE;
DROP TABLE IF EXISTS config_templates CASCADE;
DROP TABLE IF EXISTS telemetry_configs CASCADE;
DROP TABLE IF EXISTS reports CASCADE;
DROP TABLE IF EXISTS ports CASCADE;
DROP TABLE IF EXISTS devices CASCADE;
DROP TABLE IF EXISTS user_sessions CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create custom types
CREATE TYPE device_type_enum AS ENUM ('router', 'switch', 'server', 'wireless', 'firewall', 'laptop', 'desktop', 'printer');
CREATE TYPE device_status_enum AS ENUM ('active', 'inactive', 'warning', 'maintenance', 'unknown');
CREATE TYPE port_type_enum AS ENUM ('ethernet', 'fiber', 'wireless', 'serial', 'usb');
CREATE TYPE port_status_enum AS ENUM ('up', 'down', 'admin_down', 'error');
CREATE TYPE task_status_enum AS ENUM ('pending', 'running', 'completed', 'failed', 'cancelled');
CREATE TYPE report_status_enum AS ENUM ('pending', 'generating', 'completed', 'failed');
CREATE TYPE user_role_enum AS ENUM ('admin', 'operator', 'viewer', 'guest');

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    role user_role_enum DEFAULT 'viewer',
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone VARCHAR(20),
    department VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP WITH TIME ZONE,
    login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    
    CONSTRAINT users_username_length CHECK (LENGTH(username) >= 3),
    CONSTRAINT users_password_hash_length CHECK (LENGTH(password_hash) >= 60),
    CONSTRAINT users_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- User sessions table for JWT token management
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(256) NOT NULL,
    refresh_token_hash VARCHAR(256),
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_revoked BOOLEAN DEFAULT FALSE
);

-- Devices table
CREATE TABLE devices (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    device_type device_type_enum NOT NULL,
    ip_address INET NOT NULL,
    hostname VARCHAR(255),
    domain VARCHAR(255),
    username VARCHAR(50),
    password VARCHAR(100), -- Encrypted in application
    ssh_port INTEGER DEFAULT 22,
    snmp_community VARCHAR(100),
    snmp_version VARCHAR(10) DEFAULT '2c',
    status device_status_enum DEFAULT 'inactive',
    location VARCHAR(255),
    description TEXT,
    vendor VARCHAR(100),
    model VARCHAR(100),
    serial_number VARCHAR(100),
    os_version VARCHAR(100),
    firmware_version VARCHAR(100),
    management_url VARCHAR(500),
    tags JSONB DEFAULT '[]',
    configuration JSONB DEFAULT '{}',
    last_seen TIMESTAMP WITH TIME ZONE,
    last_backup TIMESTAMP WITH TIME ZONE,
    backup_config TEXT,
    monitoring_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    
    CONSTRAINT devices_name_not_empty CHECK (LENGTH(TRIM(name)) > 0),
    CONSTRAINT devices_ssh_port_valid CHECK (ssh_port > 0 AND ssh_port <= 65535),
    CONSTRAINT devices_ip_not_null CHECK (ip_address IS NOT NULL),
    CONSTRAINT devices_snmp_version_valid CHECK (snmp_version IN ('1', '2c', '3'))
);

-- Ports table
CREATE TABLE ports (
    id SERIAL PRIMARY KEY,
    device_id INTEGER NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    port_type port_type_enum NOT NULL DEFAULT 'ethernet',
    status port_status_enum DEFAULT 'down',
    admin_status port_status_enum DEFAULT 'up',
    speed BIGINT, -- Speed in bps
    duplex VARCHAR(10), -- full, half, auto
    mtu INTEGER DEFAULT 1500,
    mac_address MACADDR,
    ip_address INET,
    subnet_mask INET,
    vlan_id INTEGER,
    vlan_name VARCHAR(100),
    connected_to_port_id INTEGER REFERENCES ports(id),
    cable_type VARCHAR(50),
    cable_length DECIMAL(10,2),
    description TEXT,
    last_status_change TIMESTAMP WITH TIME ZONE,
    error_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT ports_name_device_unique UNIQUE (device_id, name),
    CONSTRAINT ports_speed_positive CHECK (speed > 0 OR speed IS NULL),
    CONSTRAINT ports_mtu_valid CHECK (mtu >= 64 AND mtu <= 9216),
    CONSTRAINT ports_vlan_id_valid CHECK (vlan_id >= 1 AND vlan_id <= 4094 OR vlan_id IS NULL),
    CONSTRAINT ports_self_connection CHECK (id != connected_to_port_id)
);

-- Inventory table
CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    device_id INTEGER NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    hardware_model VARCHAR(100),
    serial_number VARCHAR(100),
    part_number VARCHAR(100),
    os_version VARCHAR(100),
    firmware_version VARCHAR(100),
    memory_total BIGINT, -- in bytes
    memory_used BIGINT,
    storage_total BIGINT, -- in bytes
    storage_used BIGINT,
    cpu_model VARCHAR(200),
    cpu_cores INTEGER,
    cpu_speed DECIMAL(10,2), -- in GHz
    power_consumption DECIMAL(10,2), -- in watts
    temperature DECIMAL(5,2), -- in Celsius
    uptime BIGINT, -- in seconds
    software_licenses JSONB DEFAULT '[]',
    modules JSONB DEFAULT '[]',
    last_inventory_update TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    scan_duration INTEGER, -- scan time in seconds
    scan_errors JSONB DEFAULT '[]',
    
    CONSTRAINT inventory_device_unique UNIQUE (device_id),
    CONSTRAINT inventory_memory_valid CHECK (memory_used <= memory_total OR memory_used IS NULL OR memory_total IS NULL),
    CONSTRAINT inventory_storage_valid CHECK (storage_used <= storage_total OR storage_used IS NULL OR storage_total IS NULL),
    CONSTRAINT inventory_cpu_cores_positive CHECK (cpu_cores > 0 OR cpu_cores IS NULL),
    CONSTRAINT inventory_temperature_reasonable CHECK (temperature >= -50 AND temperature <= 150 OR temperature IS NULL)
);

-- Interface inventory table
CREATE TABLE interface_inventory (
    id SERIAL PRIMARY KEY,
    inventory_id INTEGER NOT NULL REFERENCES inventory(id) ON DELETE CASCADE,
    port_id INTEGER NOT NULL REFERENCES ports(id) ON DELETE CASCADE,
    mac_address MACADDR,
    speed BIGINT, -- in bps
    duplex VARCHAR(10),
    mtu INTEGER,
    rx_packets BIGINT DEFAULT 0,
    tx_packets BIGINT DEFAULT 0,
    rx_bytes BIGINT DEFAULT 0,
    tx_bytes BIGINT DEFAULT 0,
    rx_errors BIGINT DEFAULT 0,
    tx_errors BIGINT DEFAULT 0,
    rx_dropped BIGINT DEFAULT 0,
    tx_dropped BIGINT DEFAULT 0,
    last_stats_update TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT interface_inventory_unique UNIQUE (inventory_id, port_id),
    CONSTRAINT interface_stats_non_negative CHECK (
        rx_packets >= 0 AND tx_packets >= 0 AND
        rx_bytes >= 0 AND tx_bytes >= 0 AND
        rx_errors >= 0 AND tx_errors >= 0 AND
        rx_dropped >= 0 AND tx_dropped >= 0
    )
);

-- Configuration templates table
CREATE TABLE config_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    device_type device_type_enum NOT NULL,
    content TEXT NOT NULL,
    variables JSONB DEFAULT '{}',
    description TEXT,
    version VARCHAR(20) DEFAULT '1.0',
    is_active BOOLEAN DEFAULT TRUE,
    category VARCHAR(50),
    tags JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    
    CONSTRAINT config_templates_name_not_empty CHECK (LENGTH(TRIM(name)) > 0),
    CONSTRAINT config_templates_content_not_empty CHECK (LENGTH(TRIM(content)) > 0)
);

-- Provisioning tasks table
CREATE TABLE provisioning_tasks (
    id SERIAL PRIMARY KEY,
    device_id INTEGER NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    template_id INTEGER REFERENCES config_templates(id),
    status task_status_enum DEFAULT 'pending',
    config_data JSONB DEFAULT '{}',
    rendered_config TEXT,
    result JSONB DEFAULT '{}',
    error_message TEXT,
    progress INTEGER DEFAULT 0,
    priority INTEGER DEFAULT 50,
    scheduled_at TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    timeout_seconds INTEGER DEFAULT 300,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    
    CONSTRAINT provisioning_tasks_progress_valid CHECK (progress >= 0 AND progress <= 100),
    CONSTRAINT provisioning_tasks_priority_valid CHECK (priority >= 1 AND priority <= 100),
    CONSTRAINT provisioning_tasks_timeout_positive CHECK (timeout_seconds > 0),
    CONSTRAINT provisioning_tasks_retry_valid CHECK (retry_count <= max_retries)
);

-- Telemetry configurations table
CREATE TABLE telemetry_configs (
    id SERIAL PRIMARY KEY,
    device_id INTEGER NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    metrics JSONB NOT NULL DEFAULT '[]',
    collection_interval INTEGER DEFAULT 60, -- seconds
    retention_days INTEGER DEFAULT 30,
    enabled BOOLEAN DEFAULT TRUE,
    collection_method VARCHAR(20) DEFAULT 'snmp', -- snmp, ssh, api, netconf
    custom_oids JSONB DEFAULT '{}',
    thresholds JSONB DEFAULT '{}',
    last_collection TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    
    CONSTRAINT telemetry_configs_device_unique UNIQUE (device_id),
    CONSTRAINT telemetry_configs_interval_positive CHECK (collection_interval > 0),
    CONSTRAINT telemetry_configs_retention_positive CHECK (retention_days > 0),
    CONSTRAINT telemetry_configs_method_valid CHECK (collection_method IN ('snmp', 'ssh', 'api', 'netconf', 'icmp'))
);

-- Telemetry data table (time-series data)
CREATE TABLE telemetry_data (
    id BIGSERIAL PRIMARY KEY,
    device_id INTEGER NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    metric VARCHAR(100) NOT NULL,
    value DECIMAL(20,6),
    string_value TEXT,
    unit VARCHAR(20),
    labels JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    collection_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT telemetry_data_metric_not_empty CHECK (LENGTH(TRIM(metric)) > 0),
    CONSTRAINT telemetry_data_value_or_string CHECK (
        (value IS NOT NULL AND string_value IS NULL) OR
        (value IS NULL AND string_value IS NOT NULL)
    )
);

-- Reports table
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    parameters JSONB DEFAULT '{}',
    filters JSONB DEFAULT '{}',
    schedule_cron VARCHAR(100), -- cron expression for scheduled reports
    format VARCHAR(20) DEFAULT 'html', -- html, pdf, csv, json
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    generated_at TIMESTAMP WITH TIME ZONE,
    status report_status_enum DEFAULT 'pending',
    result TEXT,
    file_path VARCHAR(500),
    file_size BIGINT,
    expires_at TIMESTAMP WITH TIME ZONE,
    download_count INTEGER DEFAULT 0,
    is_public BOOLEAN DEFAULT FALSE,
    created_by INTEGER REFERENCES users(id),
    
    CONSTRAINT reports_name_not_empty CHECK (LENGTH(TRIM(name)) > 0),
    CONSTRAINT reports_format_valid CHECK (format IN ('html', 'pdf', 'csv', 'json', 'xlsx')),
    CONSTRAINT reports_file_size_positive CHECK (file_size > 0 OR file_size IS NULL)
);

-- Topology devices table (for storing topology layouts)
CREATE TABLE topology_devices (
    id SERIAL PRIMARY KEY,
    device_id INTEGER REFERENCES devices(id) ON DELETE CASCADE,
    topology_name VARCHAR(100) DEFAULT 'default',
    x_position DECIMAL(10,2) NOT NULL,
    y_position DECIMAL(10,2) NOT NULL,
    z_index INTEGER DEFAULT 1,
    rotation DECIMAL(5,2) DEFAULT 0,
    scale DECIMAL(3,2) DEFAULT 1.0,
    custom_icon VARCHAR(255),
    custom_label VARCHAR(100),
    visible BOOLEAN DEFAULT TRUE,
    locked BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT topology_devices_name_device_unique UNIQUE (topology_name, device_id),
    CONSTRAINT topology_devices_scale_positive CHECK (scale > 0),
    CONSTRAINT topology_devices_rotation_valid CHECK (rotation >= 0 AND rotation < 360)
);

-- Topology connections table
CREATE TABLE topology_connections (
    id SERIAL PRIMARY KEY,
    from_device_id INTEGER REFERENCES devices(id) ON DELETE CASCADE,
    to_device_id INTEGER REFERENCES devices(id) ON DELETE CASCADE,
    from_port_id INTEGER REFERENCES ports(id) ON DELETE SET NULL,
    to_port_id INTEGER REFERENCES ports(id) ON DELETE SET NULL,
    topology_name VARCHAR(100) DEFAULT 'default',
    connection_type VARCHAR(50) DEFAULT 'ethernet',
    label VARCHAR(100),
    color VARCHAR(7), -- hex color code
    line_style VARCHAR(20) DEFAULT 'solid', -- solid, dashed, dotted
    bandwidth BIGINT, -- in bps
    latency DECIMAL(10,3), -- in ms
    packet_loss DECIMAL(5,3), -- percentage
    is_redundant BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT topology_connections_different_devices CHECK (from_device_id != to_device_id),
    CONSTRAINT topology_connections_line_style_valid CHECK (line_style IN ('solid', 'dashed', 'dotted')),
    CONSTRAINT topology_connections_packet_loss_valid CHECK (packet_loss >= 0 AND packet_loss <= 100 OR packet_loss IS NULL)
);

-- Create indexes for better performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_active ON users(is_active);

CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_token_hash ON user_sessions(token_hash);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);

CREATE INDEX idx_devices_type ON devices(device_type);
CREATE INDEX idx_devices_status ON devices(status);
CREATE INDEX idx_devices_ip_address ON devices(ip_address);
CREATE INDEX idx_devices_name ON devices(name);
CREATE INDEX idx_devices_created_at ON devices(created_at);

CREATE INDEX idx_ports_device_id ON ports(device_id);
CREATE INDEX idx_ports_status ON ports(status);
CREATE INDEX idx_ports_connected_to ON ports(connected_to_port_id);
CREATE INDEX idx_ports_name ON ports(name);

CREATE INDEX idx_inventory_device_id ON inventory(device_id);
CREATE INDEX idx_inventory_last_update ON inventory(last_inventory_update);

CREATE INDEX idx_interface_inventory_inventory_id ON interface_inventory(inventory_id);
CREATE INDEX idx_interface_inventory_port_id ON interface_inventory(port_id);

CREATE INDEX idx_config_templates_device_type ON config_templates(device_type);
CREATE INDEX idx_config_templates_active ON config_templates(is_active);
CREATE INDEX idx_config_templates_category ON config_templates(category);

CREATE INDEX idx_provisioning_tasks_device_id ON provisioning_tasks(device_id);
CREATE INDEX idx_provisioning_tasks_status ON provisioning_tasks(status);
CREATE INDEX idx_provisioning_tasks_created_at ON provisioning_tasks(created_at);
CREATE INDEX idx_provisioning_tasks_scheduled_at ON provisioning_tasks(scheduled_at);

CREATE INDEX idx_telemetry_configs_device_id ON telemetry_configs(device_id);
CREATE INDEX idx_telemetry_configs_enabled ON telemetry_configs(enabled);

CREATE INDEX idx_telemetry_data_device_id ON telemetry_data(device_id);
CREATE INDEX idx_telemetry_data_metric ON telemetry_data(metric);
CREATE INDEX idx_telemetry_data_timestamp ON telemetry_data(timestamp);
CREATE INDEX idx_telemetry_data_device_metric_timestamp ON telemetry_data(device_id, metric, timestamp);

CREATE INDEX idx_reports_type ON reports(report_type);
CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_reports_created_at ON reports(created_at);
CREATE INDEX idx_reports_created_by ON reports(created_by);

CREATE INDEX idx_topology_devices_topology_name ON topology_devices(topology_name);
CREATE INDEX idx_topology_devices_device_id ON topology_devices(device_id);

CREATE INDEX idx_topology_connections_topology_name ON topology_connections(topology_name);
CREATE INDEX idx_topology_connections_from_device ON topology_connections(from_device_id);
CREATE INDEX idx_topology_connections_to_device ON topology_connections(to_device_id);

-- Create triggers for updated_at columns
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_devices_updated_at BEFORE UPDATE ON devices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ports_updated_at BEFORE UPDATE ON ports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_config_templates_updated_at BEFORE UPDATE ON config_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_telemetry_configs_updated_at BEFORE UPDATE ON telemetry_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_topology_devices_updated_at BEFORE UPDATE ON topology_devices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_topology_connections_updated_at BEFORE UPDATE ON topology_connections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function for automatic telemetry data cleanup
CREATE OR REPLACE FUNCTION cleanup_old_telemetry_data()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Delete telemetry data older than retention period for each device
    DELETE FROM telemetry_data 
    WHERE id IN (
        SELECT td.id 
        FROM telemetry_data td
        JOIN telemetry_configs tc ON td.device_id = tc.device_id
        WHERE td.timestamp < (CURRENT_TIMESTAMP - (tc.retention_days || ' days')::INTERVAL)
    );
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Create views for common queries
CREATE VIEW device_summary AS
SELECT 
    d.id,
    d.name,
    d.device_type,
    d.ip_address,
    d.status,
    d.location,
    d.vendor,
    d.model,
    d.last_seen,
    COUNT(p.id) as port_count,
    COUNT(CASE WHEN p.status = 'up' THEN 1 END) as active_ports,
    i.memory_used,
    i.memory_total,
    i.cpu_cores,
    i.temperature,
    i.uptime,
    d.created_at
FROM devices d
LEFT JOIN ports p ON d.id = p.device_id
LEFT JOIN inventory i ON d.id = i.device_id
GROUP BY d.id, i.memory_used, i.memory_total, i.cpu_cores, i.temperature, i.uptime;

CREATE VIEW topology_summary AS
SELECT 
    topology_name,
    COUNT(DISTINCT td.device_id) as device_count,
    COUNT(tc.id) as connection_count,
    MIN(td.created_at) as created_at,
    MAX(td.updated_at) as last_modified
FROM topology_devices td
LEFT JOIN topology_connections tc ON td.topology_name = tc.topology_name
GROUP BY topology_name;

-- Grant permissions (adjust based on your user roles)
-- These will be customized based on your specific user management needs

-- Create database statistics function
CREATE OR REPLACE FUNCTION get_database_stats()
RETURNS JSON AS $$
DECLARE
    stats JSON;
BEGIN
    SELECT json_build_object(
        'total_devices', (SELECT COUNT(*) FROM devices),
        'active_devices', (SELECT COUNT(*) FROM devices WHERE status = 'active'),
        'total_ports', (SELECT COUNT(*) FROM ports),
        'connected_ports', (SELECT COUNT(*) FROM ports WHERE connected_to_port_id IS NOT NULL),
        'total_connections', (SELECT COUNT(*) FROM topology_connections),
        'total_users', (SELECT COUNT(*) FROM users WHERE is_active = true),
        'total_reports', (SELECT COUNT(*) FROM reports),
        'total_templates', (SELECT COUNT(*) FROM config_templates WHERE is_active = true),
        'telemetry_data_points', (SELECT COUNT(*) FROM telemetry_data WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '24 hours'),
        'database_size', pg_size_pretty(pg_database_size(current_database())),
        'generated_at', CURRENT_TIMESTAMP
    ) INTO stats;
    
    RETURN stats;
END;
$$ LANGUAGE plpgsql;