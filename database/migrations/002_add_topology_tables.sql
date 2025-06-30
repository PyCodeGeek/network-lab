-- database/migrations/002_add_device_monitoring.sql
-- Add enhanced monitoring capabilities

BEGIN;

-- Add monitoring fields to devices table
ALTER TABLE devices 
ADD COLUMN IF NOT EXISTS ping_enabled BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS ping_interval INTEGER DEFAULT 30,
ADD COLUMN IF NOT EXISTS ping_timeout INTEGER DEFAULT 5,
ADD COLUMN IF NOT EXISTS ping_retries INTEGER DEFAULT 3,
ADD COLUMN IF NOT EXISTS last_ping_result BOOLEAN,
ADD COLUMN IF NOT EXISTS last_ping_time TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS ping_rtt DECIMAL(10,3);

-- Create device monitoring history table
CREATE TABLE IF NOT EXISTS device_monitoring_history (
    id BIGSERIAL PRIMARY KEY,
    device_id INTEGER NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    check_type VARCHAR(20) NOT NULL, -- ping, snmp, ssh, http
    status BOOLEAN NOT NULL,
    response_time DECIMAL(10,3),
    error_message TEXT,
    checked_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for monitoring history
CREATE INDEX IF NOT EXISTS idx_monitoring_history_device_time 
ON device_monitoring_history(device_id, checked_at);

-- Create index for monitoring history by type
CREATE INDEX IF NOT EXISTS idx_monitoring_history_type_time 
ON device_monitoring_history(check_type, checked_at);

-- Update migration info
INSERT INTO schema_migrations (version, description, applied_at) 
VALUES ('002', 'Add device monitoring capabilities', CURRENT_TIMESTAMP)
ON CONFLICT (version) DO NOTHING;

COMMIT;