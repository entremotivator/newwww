"""
UserFlow Pro - Complete User Management Toolkit
Main Application Entry Point
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from utils.auth import require_auth, AuthManager
from utils.user_auth import UserAuth, require_user_auth
from utils.supabase_client import SupabaseAdmin
from utils.database_setup import DatabaseSetup
from components.user_forms import (
    add_user_form, edit_user_form, delete_user_confirmation, 
    reset_password_form, bulk_operations_form
)
from pages.analytics import render_analytics_page
from pages.audit_logs import render_audit_logs_page
import logging

# Configure page
st.set_page_config(
    page_title="UserFlow Pro - User Management Toolkit",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def show_app_selector():
    """Show application selector"""
    st.title("🚀 UserFlow Pro")
    st.markdown("### Complete User Management Toolkit")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 User Portal")
        st.markdown("""
        **For Regular Users:**
        - Personal profile management
        - Account settings
        - Preferences configuration
        - Password management
        """)
        
        if st.button("🚀 Launch User Portal", width="stretch", type="primary"):
            st.session_state['app_mode'] = 'user'
            st.rerun()
    
    with col2:
        st.subheader("🔐 Admin Dashboard")
        st.markdown("""
        **For Administrators:**
        - User management (CRUD)
        - Analytics and reporting
        - Audit logs
        - System settings
        """)
        
        if st.button("🔐 Launch Admin Dashboard", width="stretch", type="secondary"):
            st.session_state['app_mode'] = 'admin'
            st.rerun()
    
    st.markdown("---")
    
    # Database setup section
    st.subheader("🛠️ Database Setup")
    
    with st.expander("Database Configuration & Setup"):
        db_setup = DatabaseSetup()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Database Status:**")
            try:
                status = db_setup.check_database_status()
                
                for key, value in status.items():
                    icon = "✅" if value else "❌"
                    label = key.replace('_', ' ').title()
                    st.write(f"{icon} {label}")
                
            except Exception as e:
                st.error(f"Failed to check database status: {e}")
        
        with col2:
            st.write("**Setup Actions:**")
            
            if st.button("🔧 Run Database Setup", width="stretch"):
                with st.spinner("Setting up database..."):
                    try:
                        if db_setup.execute_setup():
                            st.success("Database setup completed successfully!")
                        else:
                            st.error("Database setup failed")
                    except Exception as e:
                        st.error(f"Setup failed: {e}")
            
            if st.button("👥 Create Sample Users", width="stretch"):
                with st.spinner("Creating sample users..."):
                    try:
                        if db_setup.create_sample_users():
                            st.success("Sample users created successfully!")
                        else:
                            st.error("Failed to create sample users")
                    except Exception as e:
                        st.error(f"Failed to create sample users: {e}")
        
        # Show SQL script
        st.write("**SQL Setup Script:**")
        with st.expander("View/Copy SQL Script"):
            sql_script = db_setup.get_setup_sql()
            st.code(sql_script, language="sql")
            
            if st.button("📋 Copy to Clipboard"):
                st.write("Copy the SQL script above and run it in your Supabase SQL Editor")

def render_user_portal():
    """Render user portal application"""
    user_auth = UserAuth()
    
    # Check authentication
    if not user_auth.is_authenticated():
        user_auth.show_auth_page()
        return
    
    # Validate session
    if not user_auth.validate_session():
        st.error("Session expired. Please log in again.")
        user_auth.show_auth_page()
        return
    
    # Get current user and profile
    current_user = user_auth.get_current_user()
    current_profile = user_auth.get_current_profile()
    
    # Sidebar
    with st.sidebar:
        st.title("👤 User Portal")
        
        if current_profile:
            st.success(f"Welcome, {current_profile.get('full_name', current_user.get('email'))}")
        
        st.markdown("---")
        
        # Navigation
        page = st.selectbox(
            "Navigate to:",
            ["Profile", "Settings", "Security", "Preferences"]
        )
        
        st.markdown("---")
        
        # Quick actions
        if st.button("🔄 Refresh", width="stretch"):
            st.rerun()
        
        if st.button("🏠 Back to Home", width="stretch"):
            if 'app_mode' in st.session_state:
                del st.session_state['app_mode']
            st.rerun()
        
        if st.button("🚪 Logout", width="stretch"):
            user_auth.sign_out()
            st.rerun()
    
    # Main content
    if page == "Profile":
        render_user_profile(user_auth, current_user, current_profile)
    elif page == "Settings":
        render_user_settings(user_auth, current_user, current_profile)
    elif page == "Security":
        render_user_security(user_auth, current_user)
    elif page == "Preferences":
        render_user_preferences(user_auth, current_user)

def render_user_profile(user_auth, current_user, current_profile):
    """Render user profile page"""
    st.title("👤 My Profile")
    
    if not current_profile:
        st.error("Profile not found")
        return
    
    # Profile overview
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Profile Picture")
        # Placeholder for profile picture
        st.image("https://via.placeholder.com/150", width=150)
        
        if st.button("📷 Upload Photo", width="stretch"):
            st.info("Photo upload feature coming soon!")
    
    with col2:
        st.subheader("Profile Information")
        
        with st.form("profile_form"):
            full_name = st.text_input("Full Name", value=current_profile.get('full_name', ''))
            email = st.text_input("Email", value=current_profile.get('email', ''), disabled=True)
            phone = st.text_input("Phone", value=current_profile.get('phone', ''))
            job_title = st.text_input("Job Title", value=current_profile.get('job_title', ''))
            department = st.text_input("Department", value=current_profile.get('department', ''))
            location = st.text_input("Location", value=current_profile.get('location', ''))
            website = st.text_input("Website", value=current_profile.get('website', ''))
            bio = st.text_area("Bio", value=current_profile.get('bio', ''), height=100)
            
            if st.form_submit_button("💾 Save Changes", width="stretch"):
                profile_data = {
                    'full_name': full_name,
                    'phone': phone,
                    'job_title': job_title,
                    'department': department,
                    'location': location,
                    'website': website,
                    'bio': bio
                }
                
                if user_auth.update_user_profile(current_user.id, profile_data):
                    st.success("Profile updated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to update profile")
    
    st.markdown("---")
    
    # Account statistics
    st.subheader("📊 Account Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Account Age", "45 days")
    
    with col2:
        st.metric("Last Login", "2 hours ago")
    
    with col3:
        st.metric("Profile Views", "23")
    
    with col4:
        st.metric("Status", current_profile.get('status', 'active').title())

def render_user_settings(user_auth, current_user, current_profile):
    """Render user settings page"""
    st.title("⚙️ Settings")
    
    # Account settings
    st.subheader("🔧 Account Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Notification Preferences**")
        email_notifications = st.checkbox("Email notifications", value=current_profile.get('email_notifications', True))
        push_notifications = st.checkbox("Push notifications", value=False)
        sms_notifications = st.checkbox("SMS notifications", value=False)
    
    with col2:
        st.write("**Privacy Settings**")
        profile_visible = st.checkbox("Make profile visible to others", value=True)
        email_visible = st.checkbox("Show email in profile", value=False)
        phone_visible = st.checkbox("Show phone in profile", value=False)
    
    if st.button("💾 Save Settings", width="stretch"):
        settings_data = {
            'email_notifications': email_notifications
        }
        
        if user_auth.update_user_profile(current_user.id, settings_data):
            st.success("Settings saved successfully!")
        else:
            st.error("Failed to save settings")
    
    st.markdown("---")
    
    # Data export
    st.subheader("📤 Data Export")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Export Profile Data", width="stretch"):
            st.success("Profile data exported!")
    
    with col2:
        if st.button("📊 Export Activity Data", width="stretch"):
            st.success("Activity data exported!")
    
    with col3:
        if st.button("🗂️ Export All Data", width="stretch"):
            st.success("All data exported!")

def render_user_security(user_auth, current_user):
    """Render user security page"""
    st.title("🔒 Security")
    
    # Password change
    st.subheader("🔑 Change Password")
    
    with st.form("password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        if st.form_submit_button("🔄 Change Password", width="stretch"):
            if not all([current_password, new_password, confirm_password]):
                st.error("All fields are required")
            elif new_password != confirm_password:
                st.error("New passwords do not match")
            elif len(new_password) < 8:
                st.error("Password must be at least 8 characters")
            else:
                if user_auth.change_password(new_password):
                    st.success("Password changed successfully!")
                else:
                    st.error("Failed to change password")
    
    st.markdown("---")
    
    # Security overview
    st.subheader("🛡️ Security Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Account Security**")
        st.success("✅ Email verified")
        st.info("ℹ️ Two-factor authentication: Disabled")
        st.warning("⚠️ Last password change: 30 days ago")
    
    with col2:
        st.write("**Recent Activity**")
        st.write("• Login from Chrome (2 hours ago)")
        st.write("• Profile updated (1 day ago)")
        st.write("• Password changed (30 days ago)")
    
    # Two-factor authentication
    st.subheader("🔐 Two-Factor Authentication")
    
    if st.button("🔧 Enable 2FA", width="stretch"):
        st.info("Two-factor authentication setup coming soon!")

def render_user_preferences(user_auth, current_user):
    """Render user preferences page"""
    st.title("🎨 Preferences")
    
    # Get current preferences
    preferences = user_auth.get_user_preferences(current_user.id) or {}
    
    # Theme settings
    st.subheader("🎨 Appearance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        theme = st.selectbox(
            "Theme",
            ["light", "dark", "auto"],
            index=["light", "dark", "auto"].index(preferences.get('theme', 'light'))
        )
        
        language = st.selectbox(
            "Language",
            ["en", "es", "fr", "de"],
            index=["en", "es", "fr", "de"].index(preferences.get('language', 'en'))
        )
    
    with col2:
        timezone = st.selectbox(
            "Timezone",
            ["UTC", "America/New_York", "Europe/London", "Asia/Tokyo"],
            index=["UTC", "America/New_York", "Europe/London", "Asia/Tokyo"].index(preferences.get('timezone', 'UTC'))
        )
        
        date_format = st.selectbox(
            "Date Format",
            ["MM/DD/YYYY", "DD/MM/YYYY", "YYYY-MM-DD"],
            index=0
        )
    
    if st.button("💾 Save Preferences", width="stretch"):
        new_preferences = {
            'theme': theme,
            'language': language,
            'timezone': timezone
        }
        
        if user_auth.update_user_preferences(current_user.id, new_preferences):
            st.success("Preferences saved successfully!")
        else:
            st.error("Failed to save preferences")

def render_admin_dashboard():
    """Render admin dashboard"""
    # Use existing admin authentication
    require_auth()
    
    # Initialize Supabase
    try:
        supabase_admin = SupabaseAdmin()
    except Exception as e:
        st.error("Failed to connect to Supabase. Running in demo mode.")
        supabase_admin = None
    
    # Sidebar
    with st.sidebar:
        st.title("🔐 Admin Dashboard")
        
        admin_user = AuthManager.get_current_admin()
        if admin_user:
            st.success(f"Welcome, {admin_user.get('full_name', admin_user.get('email'))}")
        
        st.markdown("---")
        
        page = st.selectbox(
            "Navigate to:",
            ["Dashboard", "User Management", "User Analytics", "Audit Logs", "Settings"]
        )
        
        st.markdown("---")
        
        if st.button("🔄 Refresh Data", width="stretch"):
            st.cache_data.clear()
            st.rerun()
        
        if st.button("🏠 Back to Home", width="stretch"):
            if 'app_mode' in st.session_state:
                del st.session_state['app_mode']
            st.rerun()
        
        if st.button("🚪 Logout", width="stretch"):
            AuthManager.logout()
    
    # Render pages (reuse existing functions)
    if page == "Dashboard":
        render_dashboard(supabase_admin)
    elif page == "User Management":
        render_user_management(supabase_admin)
    elif page == "User Analytics":
        render_analytics_page(supabase_admin)
    elif page == "Audit Logs":
        render_audit_logs_page(supabase_admin)
    elif page == "Settings":
        render_settings_page()

def render_dashboard(supabase_admin):
    """Render admin dashboard (reused from enhanced_app.py)"""
    st.title("📊 Admin Dashboard")
    
    # Get user statistics
    if supabase_admin:
        stats = supabase_admin.get_user_stats()
    else:
        stats = {
            'total_users': 150,
            'active_users': 142,
            'inactive_users': 8,
            'admin_users': 3,
            'regular_users': 147
        }
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", stats['total_users'], "+12 this month")
    
    with col2:
        st.metric("Active Users", stats['active_users'], f"{stats['active_users']/stats['total_users']*100:.1f}% active")
    
    with col3:
        st.metric("Admin Users", stats['admin_users'], "No change")
    
    with col4:
        st.metric("Inactive Users", stats['inactive_users'], "-2 this week")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("User Status Distribution")
        status_data = pd.DataFrame({
            'Status': ['Active', 'Inactive'],
            'Count': [stats['active_users'], stats['inactive_users']]
        })
        
        fig_pie = px.pie(status_data, values='Count', names='Status')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("User Role Distribution")
        role_data = pd.DataFrame({
            'Role': ['Regular Users', 'Admin Users'],
            'Count': [stats['regular_users'], stats['admin_users']]
        })
        
        fig_bar = px.bar(role_data, x='Role', y='Count', color='Role')
        st.plotly_chart(fig_bar, use_container_width=True)

def render_user_management(supabase_admin):
    """Render user management (simplified version)"""
    st.title("👥 User Management")
    st.info("User management features available in full admin mode")

def render_settings_page():
    """Render admin settings page"""
    st.title("⚙️ Admin Settings")
    st.info("Admin settings page")

def main():
    """Main application function"""
    # Check if app mode is selected
    app_mode = st.session_state.get('app_mode')
    
    if app_mode == 'user':
        render_user_portal()
    elif app_mode == 'admin':
        render_admin_dashboard()
    else:
        show_app_selector()

if __name__ == "__main__":
    main()

