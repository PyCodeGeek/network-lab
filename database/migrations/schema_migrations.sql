-- database/migrations/schema_migrations.sql
-- Schema migrations tracking table

CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(20) PRIMARY KEY,
    description TEXT,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    execution_time INTERVAL,
    checksum VARCHAR(64)
);

-- Function to apply migration
CREATE OR REPLACE FUNCTION apply_migration(
    migration_version VARCHAR(20),
    migration_description TEXT,
    migration_sql TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
    start_time TIMESTAMP WITH TIME ZONE;
    end_time TIMESTAMP WITH TIME ZONE;
    execution_duration INTERVAL;
    migration_checksum VARCHAR(64);
BEGIN
    -- Check if migration already applied
    IF EXISTS (SELECT 1 FROM schema_migrations WHERE version = migration_version) THEN
        RAISE NOTICE 'Migration % already applied', migration_version;
        RETURN FALSE;
    END IF;
    
    start_time := CURRENT_TIMESTAMP;
    migration_checksum := encode(digest(migration_sql, 'sha256'), 'hex');
    
    -- Execute migration
    EXECUTE migration_sql;
    
    end_time := CURRENT_TIMESTAMP;
    execution_duration := end_time - start_time;
    
    -- Record migration
    INSERT INTO schema_migrations (version, description, applied_at, execution_time, checksum)
    VALUES (migration_version, migration_description, start_time, execution_duration, migration_checksum);
    
    RAISE NOTICE 'Migration % applied successfully in %', migration_version, execution_duration;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;