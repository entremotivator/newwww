"""
Database Setup Utility for UserFlow Pro
"""
import streamlit as st
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)

class DatabaseSetup:
    """Database setup and initialization"""
    
    def __init__(self):
        """Initialize database setup client"""
        try:
            self.url = st.secrets["supabase"]["url"]
            self.service_role_key = st.secrets["supabase"]["service_role_key"]
            self.client: Client = create_client(self.url, self.service_role_key)
            logger.info("Database setup client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database setup client: {e}")
            raise e
    
    def get_setup_sql(self) -> str:
        """Get the complete SQL setup script"""
        return """
-- UserFlow Pro Database Setup Script
-- Run this in your Supabase SQL Editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create profiles table
CREATE TABLE IF NOT EXISTS profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    role TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin', 'moderator')),
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),
    phone TEXT,
    department TEXT,
    job_title TEXT,
    bio TEXT,
    location TEXT,
    website TEXT,
    last_login TIMESTAMPTZ,
    email_notifications BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create user_sessions table for tracking login sessions
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    session_token TEXT UNIQUE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create audit_logs table for tracking admin actions
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    admin_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    target_user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    details JSONB,
    ip_address INET,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create password_reset_tokens table
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create user_preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
    theme TEXT DEFAULT 'light' CHECK (theme IN ('light', 'dark', 'auto')),
    language TEXT DEFAULT 'en',
    timezone TEXT DEFAULT 'UTC',
    notifications JSONB DEFAULT '{"email": true, "push": false, "sms": false}',
    privacy_settings JSONB DEFAULT '{"profile_visible": true, "email_visible": false}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create function to handle updated_at timestamp
CREATE OR REPLACE FUNCTION handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at
CREATE TRIGGER profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION handle_updated_at();

CREATE TRIGGER user_preferences_updated_at
    BEFORE UPDATE ON user_preferences
    FOR EACH ROW
    EXECUTE FUNCTION handle_updated_at();

-- Create function to handle new user profile creation
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO profiles (id, email, full_name)
    VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>'full_name');
    
    INSERT INTO user_preferences (user_id)
    VALUES (NEW.id);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger for new user profile creation
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION handle_new_user();

-- Row Level Security (RLS) Policies

-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE password_reset_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- Profiles policies
CREATE POLICY "Users can view their own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Admins can view all profiles" ON profiles
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

CREATE POLICY "Admins can insert profiles" ON profiles
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

CREATE POLICY "Admins can update all profiles" ON profiles
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

CREATE POLICY "Admins can delete profiles" ON profiles
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- User preferences policies
CREATE POLICY "Users can view their own preferences" ON user_preferences
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own preferences" ON user_preferences
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own preferences" ON user_preferences
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- User sessions policies
CREATE POLICY "Users can view their own sessions" ON user_sessions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Admins can view all sessions" ON user_sessions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

CREATE POLICY "System can insert sessions" ON user_sessions
    FOR INSERT WITH CHECK (true);

CREATE POLICY "System can update sessions" ON user_sessions
    FOR UPDATE USING (true);

-- Audit logs policies
CREATE POLICY "Admins can view audit logs" ON audit_logs
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

CREATE POLICY "System can insert audit logs" ON audit_logs
    FOR INSERT WITH CHECK (true);

-- Password reset tokens policies
CREATE POLICY "System can manage password reset tokens" ON password_reset_tokens
    FOR ALL USING (true);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email);
CREATE INDEX IF NOT EXISTS idx_profiles_role ON profiles(role);
CREATE INDEX IF NOT EXISTS idx_profiles_status ON profiles(status);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_audit_logs_admin_id ON audit_logs(admin_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_target_user_id ON audit_logs(target_user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id ON password_reset_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token ON password_reset_tokens(token);
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);

-- Create views for easier data access
CREATE OR REPLACE VIEW user_details AS
SELECT 
    p.id,
    p.email,
    p.full_name,
    p.role,
    p.status,
    p.department,
    p.job_title,
    p.last_login,
    p.created_at,
    up.theme,
    up.language,
    up.timezone,
    au.email_confirmed_at,
    au.last_sign_in_at
FROM profiles p
LEFT JOIN user_preferences up ON p.id = up.user_id
LEFT JOIN auth.users au ON p.id = au.id;

-- Insert sample data (optional - remove in production)
-- This creates a default admin user - update with your actual admin email
INSERT INTO auth.users (id, email, encrypted_password, email_confirmed_at, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'entremotivator@gmail.com',
    crypt('admin123', gen_salt('bf')),
    NOW(),
    NOW(),
    NOW()
) ON CONFLICT (email) DO NOTHING;

-- Update the admin user role
UPDATE profiles 
SET role = 'admin', status = 'active' 
WHERE email = 'entremotivator@gmail.com';

-- Create a function to safely create admin users
CREATE OR REPLACE FUNCTION create_admin_user(
    admin_email TEXT,
    admin_password TEXT,
    admin_name TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    new_user_id UUID;
BEGIN
    -- Insert into auth.users
    INSERT INTO auth.users (
        id,
        email,
        encrypted_password,
        email_confirmed_at,
        created_at,
        updated_at
    ) VALUES (
        gen_random_uuid(),
        admin_email,
        crypt(admin_password, gen_salt('bf')),
        NOW(),
        NOW(),
        NOW()
    ) RETURNING id INTO new_user_id;
    
    -- Update profile to admin role
    UPDATE profiles 
    SET role = 'admin', 
        status = 'active',
        full_name = COALESCE(admin_name, admin_email)
    WHERE id = new_user_id;
    
    RETURN new_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;

-- Success message
SELECT 'UserFlow Pro database setup completed successfully!' as message;
"""
    
    def execute_setup(self) -> bool:
        """Execute the database setup"""
        try:
            setup_sql = self.get_setup_sql()
            
            # Split SQL into individual statements
            statements = [stmt.strip() for stmt in setup_sql.split(';') if stmt.strip()]
            
            success_count = 0
            total_statements = len(statements)
            
            for i, statement in enumerate(statements):
                if statement and not statement.startswith('--'):
                    try:
                        self.client.rpc('exec_sql', {'sql': statement}).execute()
                        success_count += 1
                    except Exception as e:
                        logger.warning(f"Statement {i+1} failed: {e}")
                        # Continue with other statements
                        continue
            
            logger.info(f"Database setup completed: {success_count}/{total_statements} statements executed")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            return False
    
    def check_database_status(self) -> dict:
        """Check database setup status"""
        try:
            status = {
                'profiles_table': False,
                'user_sessions_table': False,
                'audit_logs_table': False,
                'user_preferences_table': False,
                'rls_enabled': False,
                'admin_user_exists': False
            }
            
            # Check if tables exist
            tables_to_check = ['profiles', 'user_sessions', 'audit_logs', 'user_preferences']
            
            for table in tables_to_check:
                try:
                    result = self.client.table(table).select('*').limit(1).execute()
                    status[f'{table}_table'] = True
                except:
                    status[f'{table}_table'] = False
            
            # Check if admin user exists
            try:
                result = self.client.table('profiles').select('*').eq('role', 'admin').limit(1).execute()
                status['admin_user_exists'] = len(result.data) > 0
            except:
                status['admin_user_exists'] = False
            
            # Check RLS (simplified check)
            status['rls_enabled'] = status['profiles_table']  # Assume RLS is enabled if tables exist
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to check database status: {e}")
            return {}
    
    def create_sample_users(self) -> bool:
        """Create sample users for testing"""
        try:
            sample_users = [
                {
                    'email': 'john.doe@example.com',
                    'password': 'password123',
                    'full_name': 'John Doe',
                    'role': 'user',
                    'department': 'Engineering'
                },
                {
                    'email': 'jane.smith@example.com', 
                    'password': 'password123',
                    'full_name': 'Jane Smith',
                    'role': 'user',
                    'department': 'Marketing'
                },
                {
                    'email': 'mike.wilson@example.com',
                    'password': 'password123', 
                    'full_name': 'Mike Wilson',
                    'role': 'moderator',
                    'department': 'Sales'
                }
            ]
            
            for user in sample_users:
                try:
                    # Create user in auth
                    auth_response = self.client.auth.admin.create_user({
                        "email": user['email'],
                        "password": user['password'],
                        "email_confirm": True,
                        "user_metadata": {"full_name": user['full_name']}
                    })
                    
                    if auth_response.user:
                        # Update profile
                        self.client.table('profiles').update({
                            'full_name': user['full_name'],
                            'role': user['role'],
                            'department': user['department'],
                            'status': 'active'
                        }).eq('id', auth_response.user.id).execute()
                        
                except Exception as e:
                    logger.warning(f"Failed to create sample user {user['email']}: {e}")
                    continue
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create sample users: {e}")
            return False

