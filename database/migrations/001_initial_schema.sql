-- database/migrations/001_initial_schema.sql
-- Initial schema creation (this is essentially the same as init.sql but versioned)

-- Migration: 001_initial_schema
-- Description: Create initial database schema for Network Lab Automation
-- Author: System
-- Date: 2024-01-01

BEGIN;

-- Set migration info
INSERT INTO schema_migrations (version, description, applied_at) 
VALUES ('001', 'Initial schema creation', CURRENT_TIMESTAMP)
ON CONFLICT (version) DO NOTHING;

-- (Schema creation code would go here - same as init.sql)
-- This is a placeholder for the initial schema

COMMIT;