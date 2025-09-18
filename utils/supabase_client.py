"""
Supabase client utility for admin operations
"""
import streamlit as st
from supabase import create_client, Client
from typing import Optional, Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseAdmin:
    """Supabase admin client with enhanced user management capabilities"""
    
    def __init__(self):
        """Initialize Supabase client with admin credentials"""
        try:
            self.url = st.secrets["supabase"]["url"]
            self.key = st.secrets["supabase"]["key"]
            self.service_role_key = st.secrets["supabase"]["service_role_key"]
            
            # Create client with service role for admin operations
            self.client: Client = create_client(self.url, self.service_role_key)
            self.auth_client: Client = create_client(self.url, self.key)
            
            logger.info("Supabase admin client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            st.error("Failed to connect to Supabase. Please check your configuration.")
            raise e
    
    def authenticate_admin(self, email: str, password: str) -> bool:
        """Authenticate admin user"""
        try:
            response = self.auth_client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                # Check if user has admin role
                user_data = self.get_user_profile(response.user.id)
                if user_data and user_data.get('role') == 'admin':
                    st.session_state['admin_user'] = response.user
                    st.session_state['admin_authenticated'] = True
                    return True
                else:
                    st.error("Access denied. Admin privileges required.")
                    return False
            return False
        except Exception as e:
            logger.error(f"Admin authentication failed: {e}")
            st.error(f"Authentication failed: {str(e)}")
            return False
    
    def sign_out_admin(self):
        """Sign out admin user"""
        try:
            self.auth_client.auth.sign_out()
            if 'admin_user' in st.session_state:
                del st.session_state['admin_user']
            if 'admin_authenticated' in st.session_state:
                del st.session_state['admin_authenticated']
            return True
        except Exception as e:
            logger.error(f"Sign out failed: {e}")
            return False
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users from auth.users table"""
        try:
            # Use admin API to get all users
            response = self.client.auth.admin.list_users()
            return response if response else []
        except Exception as e:
            logger.error(f"Failed to fetch users: {e}")
            st.error(f"Failed to fetch users: {str(e)}")
            return []
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile from profiles table"""
        try:
            response = self.client.table('profiles').select('*').eq('id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to fetch user profile: {e}")
            return None
    
    def create_user(self, email: str, password: str, user_data: Dict[str, Any]) -> bool:
        """Create a new user"""
        try:
            # Create user in auth
            response = self.client.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True
            })
            
            if response.user:
                # Create profile
                profile_data = {
                    'id': response.user.id,
                    'email': email,
                    'full_name': user_data.get('full_name', ''),
                    'role': user_data.get('role', 'user'),
                    'status': user_data.get('status', 'active'),
                    'created_at': response.user.created_at
                }
                
                self.client.table('profiles').insert(profile_data).execute()
                logger.info(f"User created successfully: {email}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            st.error(f"Failed to create user: {str(e)}")
            return False
    
    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """Update user information"""
        try:
            # Update auth user if email or password changed
            auth_updates = {}
            if 'email' in user_data:
                auth_updates['email'] = user_data['email']
            if 'password' in user_data and user_data['password']:
                auth_updates['password'] = user_data['password']
            
            if auth_updates:
                self.client.auth.admin.update_user_by_id(user_id, auth_updates)
            
            # Update profile
            profile_updates = {k: v for k, v in user_data.items() if k not in ['password']}
            if profile_updates:
                self.client.table('profiles').update(profile_updates).eq('id', user_id).execute()
            
            logger.info(f"User updated successfully: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update user: {e}")
            st.error(f"Failed to update user: {str(e)}")
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        try:
            # Delete from profiles first
            self.client.table('profiles').delete().eq('id', user_id).execute()
            
            # Delete from auth
            self.client.auth.admin.delete_user(user_id)
            
            logger.info(f"User deleted successfully: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete user: {e}")
            st.error(f"Failed to delete user: {str(e)}")
            return False
    
    def reset_user_password(self, email: str) -> bool:
        """Send password reset email"""
        try:
            self.auth_client.auth.reset_password_email(email)
            logger.info(f"Password reset email sent to: {email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send password reset: {e}")
            st.error(f"Failed to send password reset: {str(e)}")
            return False
    
    def get_user_stats(self) -> Dict[str, int]:
        """Get user statistics"""
        try:
            users = self.get_all_users()
            profiles_response = self.client.table('profiles').select('role, status').execute()
            profiles = profiles_response.data if profiles_response.data else []
            
            stats = {
                'total_users': len(users),
                'active_users': len([p for p in profiles if p.get('status') == 'active']),
                'inactive_users': len([p for p in profiles if p.get('status') == 'inactive']),
                'admin_users': len([p for p in profiles if p.get('role') == 'admin']),
                'regular_users': len([p for p in profiles if p.get('role') == 'user'])
            }
            return stats
        except Exception as e:
            logger.error(f"Failed to get user stats: {e}")
            return {'total_users': 0, 'active_users': 0, 'inactive_users': 0, 'admin_users': 0, 'regular_users': 0}
    
    def search_users(self, query: str) -> List[Dict[str, Any]]:
        """Search users by email or name"""
        try:
            response = self.client.table('profiles').select('*').or_(
                f'email.ilike.%{query}%,full_name.ilike.%{query}%'
            ).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to search users: {e}")
            return []
    
    def bulk_update_users(self, user_ids: List[str], updates: Dict[str, Any]) -> bool:
        """Bulk update multiple users"""
        try:
            for user_id in user_ids:
                self.update_user(user_id, updates)
            logger.info(f"Bulk updated {len(user_ids)} users")
            return True
        except Exception as e:
            logger.error(f"Failed to bulk update users: {e}")
            return False
    
    def export_users_data(self) -> List[Dict[str, Any]]:
        """Export all users data"""
        try:
            response = self.client.table('profiles').select('*').execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to export users data: {e}")
            return []

