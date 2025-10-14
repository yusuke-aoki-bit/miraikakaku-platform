-- ============================================================
-- Phase 6: Authentication & User Management Schema
-- ============================================================

-- Drop existing objects if they exist
DROP TABLE IF EXISTS user_sessions CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP FUNCTION IF EXISTS update_timestamp() CASCADE;

-- ============================================================
-- Users Table
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,

    CONSTRAINT chk_username_length CHECK (char_length(username) >= 3),
    CONSTRAINT chk_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- ============================================================
-- User Sessions Table (for JWT token management)
-- ============================================================
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_jti VARCHAR(255) UNIQUE NOT NULL,
    device_info TEXT,
    ip_address VARCHAR(45),
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoked BOOLEAN DEFAULT false,

    CONSTRAINT chk_expires_future CHECK (expires_at > created_at)
);

-- ============================================================
-- Indexes
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(token_jti);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON user_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_sessions_active ON user_sessions(user_id, expires_at) WHERE revoked = false;

-- ============================================================
-- Timestamp Update Trigger Function
-- ============================================================
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- Triggers
-- ============================================================
DROP TRIGGER IF EXISTS update_users_timestamp ON users;
CREATE TRIGGER update_users_timestamp
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- ============================================================
-- Insert Demo User (for backward compatibility)
-- ============================================================
INSERT INTO users (username, email, password_hash, full_name, is_active, is_admin)
VALUES (
    'demo_user',
    'demo@miraikakaku.com',
    -- Bcrypt hash of 'demo123' (DO NOT use in production)
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYpPxvz4Q3e',
    'Demo User',
    true,
    false
)
ON CONFLICT (username) DO NOTHING;

-- ============================================================
-- Migration: Add user_id to existing tables
-- ============================================================

-- Add user_id to portfolio_holdings if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'portfolio_holdings' AND column_name = 'user_id_fk'
    ) THEN
        ALTER TABLE portfolio_holdings ADD COLUMN user_id_fk INTEGER;
        ALTER TABLE portfolio_holdings ADD CONSTRAINT fk_portfolio_user
            FOREIGN KEY (user_id_fk) REFERENCES users(id) ON DELETE CASCADE;

        -- Migrate existing data to demo_user
        UPDATE portfolio_holdings
        SET user_id_fk = (SELECT id FROM users WHERE username = 'demo_user')
        WHERE user_id = 'demo_user';
    END IF;
END $$;

-- Add user_id to watchlist if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'watchlist' AND column_name = 'user_id_fk'
    ) THEN
        ALTER TABLE watchlist ADD COLUMN user_id_fk INTEGER;
        ALTER TABLE watchlist ADD CONSTRAINT fk_watchlist_user
            FOREIGN KEY (user_id_fk) REFERENCES users(id) ON DELETE CASCADE;

        -- Migrate existing data to demo_user
        UPDATE watchlist
        SET user_id_fk = (SELECT id FROM users WHERE username = 'demo_user')
        WHERE user_id = 'demo_user';
    END IF;
END $$;

-- ============================================================
-- Helper Functions
-- ============================================================

-- Function to get user by username
CREATE OR REPLACE FUNCTION get_user_by_username(p_username VARCHAR)
RETURNS TABLE (
    id INTEGER,
    username VARCHAR,
    email VARCHAR,
    full_name VARCHAR,
    is_active BOOLEAN,
    is_admin BOOLEAN,
    created_at TIMESTAMP,
    last_login TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT u.id, u.username, u.email, u.full_name, u.is_active, u.is_admin, u.created_at, u.last_login
    FROM users u
    WHERE u.username = p_username AND u.is_active = true;
END;
$$ LANGUAGE plpgsql;

-- Function to revoke user session
CREATE OR REPLACE FUNCTION revoke_session(p_token_jti VARCHAR)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE user_sessions
    SET revoked = true
    WHERE token_jti = p_token_jti;

    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Function to cleanup expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM user_sessions
    WHERE expires_at < CURRENT_TIMESTAMP OR revoked = true;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- Verify Schema Application
-- ============================================================
SELECT 'Authentication schema applied successfully!' as message;
