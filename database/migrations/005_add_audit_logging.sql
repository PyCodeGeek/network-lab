-- database/migrations/005_add_audit_logging.sql
-- Add comprehensive audit logging

BEGIN;

-- Create audit log table
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    username VARCHAR(64),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id INTEGER,
    resource_name VARCHAR(255),
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    session_id UUID,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    additional_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for audit logs
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_type ON audit_logs(resource_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_id ON audit_logs(resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_success ON audit_logs(success);

-- Create function to log audit events
CREATE OR REPLACE FUNCTION log_audit_event(
    p_user_id INTEGER,
    p_username VARCHAR(64),
    p_action VARCHAR(100),
    p_resource_type VARCHAR(50),
    p_resource_id INTEGER,
    p_resource_name VARCHAR(255),
    p_old_values JSONB DEFAULT NULL,
    p_new_values JSONB DEFAULT NULL,
    p_ip_address INET DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL,
    p_session_id UUID DEFAULT NULL,
    p_success BOOLEAN DEFAULT TRUE,
    p_error_message TEXT DEFAULT NULL,
    p_additional_data JSONB DEFAULT '{}'
)

RETURNS BIGINT AS $$
DECLARE
    audit_id BIGINT;
BEGIN
    INSERT INTO audit_logs (
        user_id, username, action, resource_type, resource_id, resource_name,
        old_values, new_values, ip_address, user_agent, session_id,
        success, error_message, additional_data
    ) VALUES (
        p_user_id, p_username, p_action, p_resource_type, p_resource_id, p_resource_name,
        p_old_values, p_new_values, p_ip_address, p_user_agent, p_session_id,
        p_success, p_error_message, p_additional_data
    ) RETURNING id INTO audit_id;
    
    RETURN audit_id;
END;
$$ LANGUAGE plpgsql;

-- Create audit triggers for key tables
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        PERFORM log_audit_event(
            NULL, -- user_id would be set by application
            NULL, -- username would be set by application
            'DELETE',
            TG_TABLE_NAME,
            OLD.id,
            COALESCE(OLD.name, OLD.id::text),
            row_to_json(OLD),
            NULL
        );
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        PERFORM log_audit_event(
            NULL, -- user_id would be set by application
            NULL, -- username would be set by application
            'UPDATE',
            TG_TABLE_NAME,
            NEW.id,
            COALESCE(NEW.name, NEW.id::text),
            row_to_json(OLD),
            row_to_json(NEW)
        );
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        PERFORM log_audit_event(
            NULL, -- user_id would be set by application
            NULL, -- username would be set by application
            'CREATE',
            TG_TABLE_NAME,
            NEW.id,
            COALESCE(NEW.name, NEW.id::text),
            NULL,
            row_to_json(NEW)
        );
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create audit triggers for key tables
CREATE TRIGGER audit_devices_trigger
    AFTER INSERT OR UPDATE OR DELETE ON devices
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_users_trigger
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_config_templates_trigger
    AFTER INSERT OR UPDATE OR DELETE ON config_templates
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- Create function for audit log cleanup
CREATE OR REPLACE FUNCTION cleanup_old_audit_logs(retention_days INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM audit_logs 
    WHERE created_at < (CURRENT_TIMESTAMP - (retention_days || ' days')::INTERVAL);
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Update migration info
INSERT INTO schema_migrations (version, description, applied_at) 
VALUES ('005', 'Add comprehensive audit logging', CURRENT_TIMESTAMP)
ON CONFLICT (version) DO NOTHING;

COMMIT;
