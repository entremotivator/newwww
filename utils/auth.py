"""
Authentication utilities for Streamlit admin app
"""
import streamlit as st
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class AuthManager:
    """Authentication manager for admin sessions"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return hashlib.sha256(password.encode()).hexdigest() == hashed
    
    @staticmethod
    def generate_session_token() -> str:
        """Generate secure session token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def is_admin_authenticated() -> bool:
        """Check if admin is authenticated"""
        return st.session_state.get('admin_authenticated', False)
    
    @staticmethod
    def get_current_admin() -> Optional[Dict[str, Any]]:
        """Get current admin user"""
        return st.session_state.get('admin_user')
    
    @staticmethod
    def require_admin_auth():
        """Decorator to require admin authentication"""
        if not AuthManager.is_admin_authenticated():
            st.error("Please log in as an administrator to access this page.")
            st.stop()
    
    @staticmethod
    def logout():
        """Logout current admin"""
        for key in ['admin_authenticated', 'admin_user', 'session_token']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    
    @staticmethod
    def create_session(user_data: Dict[str, Any]) -> str:
        """Create new session"""
        token = AuthManager.generate_session_token()
        st.session_state['session_token'] = token
        st.session_state['admin_user'] = user_data
        st.session_state['admin_authenticated'] = True
        st.session_state['session_created'] = datetime.now()
        return token
    
    @staticmethod
    def validate_session() -> bool:
        """Validate current session"""
        if not st.session_state.get('session_token'):
            return False
        
        session_created = st.session_state.get('session_created')
        if not session_created:
            return False
        
        # Check if session is expired (24 hours)
        if datetime.now() - session_created > timedelta(hours=24):
            AuthManager.logout()
            return False
        
        return True
    
    @staticmethod
    def get_user_ip() -> str:
        """Get user IP address"""
        # In a real deployment, you might get this from headers
        return "127.0.0.1"
    
    @staticmethod
    def log_admin_action(action: str, details: Dict[str, Any] = None):
        """Log admin action for audit trail"""
        admin_user = AuthManager.get_current_admin()
        if admin_user:
            log_entry = {
                'admin_id': admin_user.get('id'),
                'admin_email': admin_user.get('email'),
                'action': action,
                'details': details or {},
                'timestamp': datetime.now().isoformat(),
                'ip_address': AuthManager.get_user_ip()
            }
            
            # Store in session state for now (in production, store in database)
            if 'audit_logs' not in st.session_state:
                st.session_state['audit_logs'] = []
            st.session_state['audit_logs'].append(log_entry)
            
            logger.info(f"Admin action logged: {action} by {admin_user.get('email')}")

def login_form():
    """Render login form"""
    st.title("🔐 Admin Login")
    
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="admin@example.com")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", use_container_width=True)
        
        if submit:
            if not email or not password:
                st.error("Please enter both email and password")
                return False
            
            # Try to authenticate with Supabase
            try:
                from utils.supabase_client import SupabaseAdmin
                supabase_admin = SupabaseAdmin()
                
                if supabase_admin.authenticate_admin(email, password):
                    st.success("Login successful!")
                    st.rerun()
                    return True
                else:
                    st.error("Invalid credentials or insufficient privileges")
                    return False
            except Exception as e:
                # Fallback to default admin credentials for demo
                default_email = st.secrets.get("admin", {}).get("default_email", "entremotivator@gmail.com")
                default_password = st.secrets.get("admin", {}).get("default_password", "admin123")
                
                if email == default_email and password == default_password:
                    # Create mock admin user
                    admin_user = {
                        'id': 'demo-admin-id',
                        'email': email,
                        'full_name': 'Demo Administrator',
                        'role': 'admin'
                    }
                    AuthManager.create_session(admin_user)
                    st.success("Login successful! (Demo mode)")
                    st.rerun()
                    return True
                else:
                    st.error("Invalid credentials")
                    return False
    
    # Demo credentials info
    with st.expander("Demo Credentials"):
        st.info("""
        **Demo Login:**
        - Email: entremotivator@gmail.com
        - Password: admin123
        
        **Note:** Configure your Supabase credentials in `.streamlit/secrets.toml` for full functionality.
        """)
    
    return False

def require_auth():
    """Require authentication for protected pages"""
    if not AuthManager.is_admin_authenticated():
        login_form()
        st.stop()
    
    # Validate session
    if not AuthManager.validate_session():
        st.error("Session expired. Please log in again.")
        st.stop()

