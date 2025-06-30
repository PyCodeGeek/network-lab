-- database/migrations/003_add_network_discovery.sql
-- Add network discovery and scanning capabilities

BEGIN;

-- Create network discovery scans table
CREATE TABLE IF NOT EXISTS network_discovery_scans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    network_range CIDR NOT NULL,
    scan_type VARCHAR(20) DEFAULT 'ping', -- ping, arp, nmap
    status VARCHAR(20) DEFAULT 'pending', -- pending, running, completed, failed
    progress INTEGER DEFAULT 0,
    total_hosts INTEGER,
    discovered_hosts INTEGER DEFAULT 0,
    scan_options JSONB DEFAULT '{}',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id)
);

-- Create discovered devices table
CREATE TABLE IF NOT EXISTS discovered_devices (
    id SERIAL PRIMARY KEY,
    scan_id INTEGER NOT NULL REFERENCES network_discovery_scans(id) ON DELETE CASCADE,
    ip_address INET NOT NULL,
    hostname VARCHAR(255),
    mac_address MACADDR,
    vendor VARCHAR(100),
    device_type VARCHAR(50),
    os_guess VARCHAR(100),
    open_ports INTEGER[],
    response_time DECIMAL(10,3),
    is_managed BOOLEAN DEFAULT FALSE,
    device_id INTEGER REFERENCES devices(id),
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT discovered_devices_scan_ip_unique UNIQUE (scan_id, ip_address)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_discovery_scans_status ON network_discovery_scans(status);
CREATE INDEX IF NOT EXISTS idx_discovery_scans_created_at ON network_discovery_scans(created_at);
CREATE INDEX IF NOT EXISTS idx_discovered_devices_scan_id ON discovered_devices(scan_id);
CREATE INDEX IF NOT EXISTS idx_discovered_devices_ip ON discovered_devices(ip_address);
CREATE INDEX IF NOT EXISTS idx_discovered_devices_managed ON discovered_devices(is_managed);

-- Update migration info
INSERT INTO schema_migrations (version, description, applied_at) 
VALUES ('003', 'Add network discovery and scanning', CURRENT_TIMESTAMP)
ON CONFLICT (version) DO NOTHING;

COMMIT;