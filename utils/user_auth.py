"""
Regular User Authentication for UserFlow Pro
"""
import streamlit as st
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class UserAuth:
    """Regular user authentication manager"""
    
    def __init__(self):
        """Initialize user auth client"""
        try:
            self.url = st.secrets["supabase"]["url"]
            self.key = st.secrets["supabase"]["key"]
            self.client: Client = create_client(self.url, self.key)
            logger.info("User auth client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize user auth client: {e}")
            raise e
    
    def sign_up(self, email: str, password: str, full_name: str = "") -> bool:
        """Sign up a new user"""
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "full_name": full_name
                    }
                }
            })
            
            if response.user:
                st.session_state['user'] = response.user
                st.session_state['user_authenticated'] = True
                st.session_state['session_created'] = datetime.now()
                return True
            return False
            
        except Exception as e:
            logger.error(f"Sign up failed: {e}")
            st.error(f"Sign up failed: {str(e)}")
            return False
    
    def sign_in(self, email: str, password: str) -> bool:
        """Sign in user"""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                # Get user profile
                profile = self.get_user_profile(response.user.id)
                
                st.session_state['user'] = response.user
                st.session_state['user_profile'] = profile
                st.session_state['user_authenticated'] = True
                st.session_state['session_created'] = datetime.now()
                
                # Update last login
                self.update_last_login(response.user.id)
                
                return True
            return False
            
        except Exception as e:
            logger.error(f"Sign in failed: {e}")
            st.error(f"Sign in failed: {str(e)}")
            return False
    
    def sign_out(self) -> bool:
        """Sign out user"""
        try:
            self.client.auth.sign_out()
            
            # Clear session state
            keys_to_clear = ['user', 'user_profile', 'user_authenticated', 'session_created']
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            
            return True
            
        except Exception as e:
            logger.error(f"Sign out failed: {e}")
            return False
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile"""
        try:
            response = self.client.table('profiles').select('*').eq('id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            return None
    
    def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Update user profile"""
        try:
            self.client.table('profiles').update(profile_data).eq('id', user_id).execute()
            
            # Update session state
            if 'user_profile' in st.session_state:
                st.session_state['user_profile'].update(profile_data)
            
            return True
        except Exception as e:
            logger.error(f"Failed to update user profile: {e}")
            return False
    
    def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        try:
            self.client.table('profiles').update({
                'last_login': datetime.now().isoformat()
            }).eq('id', user_id).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to update last login: {e}")
            return False
    
    def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user preferences"""
        try:
            response = self.client.table('user_preferences').select('*').eq('user_id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to get user preferences: {e}")
            return None
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Update user preferences"""
        try:
            # Check if preferences exist
            existing = self.get_user_preferences(user_id)
            
            if existing:
                self.client.table('user_preferences').update(preferences).eq('user_id', user_id).execute()
            else:
                preferences['user_id'] = user_id
                self.client.table('user_preferences').insert(preferences).execute()
            
            return True
        except Exception as e:
            logger.error(f"Failed to update user preferences: {e}")
            return False
    
    def reset_password(self, email: str) -> bool:
        """Send password reset email"""
        try:
            self.client.auth.reset_password_email(email)
            return True
        except Exception as e:
            logger.error(f"Password reset failed: {e}")
            return False
    
    def change_password(self, new_password: str) -> bool:
        """Change user password"""
        try:
            self.client.auth.update_user({"password": new_password})
            return True
        except Exception as e:
            logger.error(f"Password change failed: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return st.session_state.get('user_authenticated', False)
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user"""
        return st.session_state.get('user')
    
    def get_current_profile(self) -> Optional[Dict[str, Any]]:
        """Get current user profile"""
        return st.session_state.get('user_profile')
    
    def validate_session(self) -> bool:
        """Validate current session"""
        if not self.is_authenticated():
            return False
        
        session_created = st.session_state.get('session_created')
        if not session_created:
            return False
        
        # Check if session is expired (24 hours)
        if datetime.now() - session_created > timedelta(hours=24):
            self.sign_out()
            return False
        
        return True
    
    def require_auth(self):
        """Require authentication for protected pages"""
        if not self.is_authenticated() or not self.validate_session():
            self.show_auth_page()
            st.stop()
    
    def show_auth_page(self):
        """Show authentication page"""
        st.title("🚀 Welcome to UserFlow Pro")
        st.markdown("### Your Personal User Management Toolkit")
        
        # Create tabs for login and signup
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
        
        with tab1:
            self.show_login_form()
        
        with tab2:
            self.show_signup_form()
    
    def show_login_form(self):
        """Show login form"""
        st.subheader("Login to Your Account")
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="your.email@example.com")
            password = st.text_input("Password", type="password")
            remember_me = st.checkbox("Remember me")
            
            col1, col2 = st.columns(2)
            
            with col1:
                login_button = st.form_submit_button("Login", width="stretch")
            
            with col2:
                forgot_password = st.form_submit_button("Forgot Password?", width="stretch")
            
            if login_button:
                if not email or not password:
                    st.error("Please enter both email and password")
                    return
                
                if self.sign_in(email, password):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid email or password")
            
            if forgot_password:
                if email:
                    if self.reset_password(email):
                        st.success("Password reset email sent!")
                    else:
                        st.error("Failed to send reset email")
                else:
                    st.error("Please enter your email address")
    
    def show_signup_form(self):
        """Show signup form"""
        st.subheader("Create New Account")
        
        with st.form("signup_form"):
            full_name = st.text_input("Full Name", placeholder="John Doe")
            email = st.text_input("Email", placeholder="your.email@example.com")
            password = st.text_input("Password", type="password", help="Minimum 8 characters")
            confirm_password = st.text_input("Confirm Password", type="password")
            agree_terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
            
            signup_button = st.form_submit_button("Create Account", width="stretch")
            
            if signup_button:
                # Validation
                errors = []
                
                if not full_name:
                    errors.append("Full name is required")
                if not email:
                    errors.append("Email is required")
                if not password:
                    errors.append("Password is required")
                elif len(password) < 8:
                    errors.append("Password must be at least 8 characters")
                if password != confirm_password:
                    errors.append("Passwords do not match")
                if not agree_terms:
                    errors.append("You must agree to the terms")
                
                if errors:
                    for error in errors:
                        st.error(error)
                    return
                
                if self.sign_up(email, password, full_name):
                    st.success("Account created successfully! Please check your email for verification.")
                    st.rerun()
                else:
                    st.error("Failed to create account")

def require_user_auth():
    """Decorator function to require user authentication"""
    user_auth = UserAuth()
    user_auth.require_auth()

