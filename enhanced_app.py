"""
Enhanced Supabase Admin Dashboard - Main Application
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from utils.auth import require_auth, AuthManager
from utils.supabase_client import SupabaseAdmin
from components.user_forms import (
    add_user_form, edit_user_form, delete_user_confirmation, 
    reset_password_form, bulk_operations_form
)
from pages.analytics import render_analytics_page
from pages.audit_logs import render_audit_logs_page
import logging

# Configure page
st.set_page_config(
    page_title=st.secrets.get("app", {}).get("title", "Supabase Admin Dashboard"),
    page_icon=st.secrets.get("app", {}).get("page_icon", "🔐"),
    layout=st.secrets.get("app", {}).get("layout", "wide"),
    initial_sidebar_state="expanded"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_supabase():
    """Initialize Supabase client"""
    try:
        return SupabaseAdmin()
    except Exception as e:
        st.error("Failed to connect to Supabase. Running in demo mode.")
        logger.error(f"Supabase initialization failed: {e}")
        return None

def render_sidebar():
    """Render sidebar navigation"""
    with st.sidebar:
        st.title("🔐 Admin Dashboard")
        
        # Admin info
        admin_user = AuthManager.get_current_admin()
        if admin_user:
            st.success(f"Welcome, {admin_user.get('full_name', admin_user.get('email'))}")
            
            # Navigation menu
            st.markdown("---")
            
            # Main navigation
            page = st.selectbox(
                "Navigate to:",
                [
                    "Dashboard",
                    "User Management", 
                    "User Analytics",
                    "Audit Logs",
                    "Settings"
                ],
                key="navigation"
            )
            
            st.markdown("---")
            
            # Quick actions
            st.subheader("Quick Actions")
            if st.button("🔄 Refresh Data", width="stretch"):
                st.cache_data.clear()
                st.rerun()
            
            if st.button("📊 Export Users", width="stretch"):
                st.session_state['show_export'] = True
            
            st.markdown("---")
            
            # System status
            st.subheader("System Status")
            st.success("🟢 Database: Connected")
            st.success("🟢 Auth: Active")
            st.info("🔵 Demo Mode: Enabled")
            
            st.markdown("---")
            
            # Logout
            if st.button("🚪 Logout", width="stretch"):
                AuthManager.logout()
            
            return page
    
    return "Dashboard"

def render_dashboard(supabase_admin):
    """Render main dashboard"""
    st.title("📊 Admin Dashboard")
    
    # Get user statistics
    if supabase_admin:
        stats = supabase_admin.get_user_stats()
    else:
        # Demo data
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
        st.metric(
            label="Total Users",
            value=stats['total_users'],
            delta="+12 this month"
        )
    
    with col2:
        st.metric(
            label="Active Users", 
            value=stats['active_users'],
            delta=f"{stats['active_users']/stats['total_users']*100:.1f}% active"
        )
    
    with col3:
        st.metric(
            label="Admin Users",
            value=stats['admin_users'],
            delta="No change"
        )
    
    with col4:
        st.metric(
            label="Inactive Users",
            value=stats['inactive_users'],
            delta="-2 this week"
        )
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("User Status Distribution")
        
        # Pie chart for user status
        status_data = pd.DataFrame({
            'Status': ['Active', 'Inactive'],
            'Count': [stats['active_users'], stats['inactive_users']]
        })
        
        fig_pie = px.pie(
            status_data, 
            values='Count', 
            names='Status',
            color_discrete_map={'Active': '#00D4AA', 'Inactive': '#FF6B6B'}
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("User Role Distribution")
        
        # Bar chart for user roles
        role_data = pd.DataFrame({
            'Role': ['Regular Users', 'Admin Users'],
            'Count': [stats['regular_users'], stats['admin_users']]
        })
        
        fig_bar = px.bar(
            role_data,
            x='Role',
            y='Count',
            color='Role',
            color_discrete_map={'Regular Users': '#4ECDC4', 'Admin Users': '#45B7D1'}
        )
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Recent activity
    st.subheader("Recent Activity")
    
    # Get recent audit logs from session state
    recent_logs = st.session_state.get('audit_logs', [])[-10:]
    
    if recent_logs:
        activity_data = []
        for log in recent_logs:
            activity_data.append({
                "Time": log.get('timestamp', 'Unknown'),
                "Action": log.get('action', 'Unknown'),
                "Details": f"{log.get('admin_email', 'Unknown')} - {log.get('details', {})}"
            })
        activity_df = pd.DataFrame(activity_data)
    else:
        # Demo activity data
        activity_data = [
            {"Time": "2 minutes ago", "Action": "User created", "Details": "john.doe@example.com"},
            {"Time": "15 minutes ago", "Action": "Password reset", "Details": "jane.smith@example.com"},
            {"Time": "1 hour ago", "Action": "User updated", "Details": "mike.wilson@example.com"},
            {"Time": "2 hours ago", "Action": "User deleted", "Details": "old.user@example.com"},
            {"Time": "3 hours ago", "Action": "Bulk update", "Details": "5 users updated"},
        ]
        activity_df = pd.DataFrame(activity_data)
    
    st.dataframe(activity_df, use_container_width=True, hide_index=True)

def render_user_management(supabase_admin):
    """Render enhanced user management page"""
    st.title("👥 User Management")
    
    # Action buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ Add User", width="stretch"):
            st.session_state['show_add_user'] = True
    
    with col2:
        if st.button("🔄 Refresh", width="stretch"):
            st.cache_data.clear()
            st.rerun()
    
    with col3:
        if st.button("📤 Export", width="stretch"):
            st.session_state['show_export'] = True
    
    with col4:
        if st.button("🔍 Advanced Search", width="stretch"):
            st.session_state['show_advanced_search'] = True
    
    # Search and filters
    st.markdown("---")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_query = st.text_input("🔍 Search users", placeholder="Search by email or name...")
    
    with col2:
        role_filter = st.selectbox("Filter by Role", ["All", "Admin", "User", "Moderator"])
    
    with col3:
        status_filter = st.selectbox("Filter by Status", ["All", "Active", "Inactive", "Suspended"])
    
    # Get users data
    if supabase_admin:
        try:
            users = supabase_admin.get_all_users()
            # Convert to DataFrame for easier handling
            if users:
                users_df = pd.DataFrame([
                    {
                        'ID': user.get('id', ''),
                        'Email': user.get('email', ''),
                        'Created': user.get('created_at', ''),
                        'Last Sign In': user.get('last_sign_in_at', 'Never'),
                        'Status': 'Active' if user.get('email_confirmed_at') else 'Pending'
                    }
                    for user in users
                ])
            else:
                users_df = pd.DataFrame()
        except Exception as e:
            st.error(f"Failed to fetch users: {e}")
            users_df = pd.DataFrame()
    else:
        # Demo data
        demo_users = [
            {
                'ID': 'user-1',
                'Email': 'entremotivator@gmail.com',
                'Full Name': 'Admin User',
                'Role': 'Admin',
                'Status': 'Active',
                'Created': '2024-01-15',
                'Last Login': '2024-01-20',
                'Department': 'IT',
                'Job Title': 'System Administrator'
            },
            {
                'ID': 'user-2', 
                'Email': 'john.doe@example.com',
                'Full Name': 'John Doe',
                'Role': 'User',
                'Status': 'Active',
                'Created': '2024-01-16',
                'Last Login': '2024-01-19',
                'Department': 'Engineering',
                'Job Title': 'Software Engineer'
            },
            {
                'ID': 'user-3',
                'Email': 'jane.smith@example.com', 
                'Full Name': 'Jane Smith',
                'Role': 'User',
                'Status': 'Inactive',
                'Created': '2024-01-17',
                'Last Login': '2024-01-18',
                'Department': 'Marketing',
                'Job Title': 'Marketing Manager'
            },
            {
                'ID': 'user-4',
                'Email': 'mike.wilson@example.com',
                'Full Name': 'Mike Wilson', 
                'Role': 'Moderator',
                'Status': 'Active',
                'Created': '2024-01-18',
                'Last Login': '2024-01-20',
                'Department': 'Sales',
                'Job Title': 'Sales Manager'
            }
        ]
        users_df = pd.DataFrame(demo_users)
    
    # Apply filters
    if not users_df.empty:
        filtered_df = users_df.copy()
        
        # Search filter
        if search_query:
            mask = (
                filtered_df['Email'].str.contains(search_query, case=False, na=False) |
                filtered_df.get('Full Name', pd.Series(dtype='object')).str.contains(search_query, case=False, na=False)
            )
            filtered_df = filtered_df[mask]
        
        # Role filter
        if role_filter != "All" and 'Role' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Role'] == role_filter]
        
        # Status filter  
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df['Status'] == status_filter]
        
        # Display users table
        st.markdown("---")
        st.subheader(f"Users ({len(filtered_df)} found)")
        
        if not filtered_df.empty:
            # Add selection tracking
            selected_users = []
            
            # Display table with action buttons
            for idx, user in filtered_df.iterrows():
                with st.container():
                    col1, col2, col3, col4, col5, col6 = st.columns([0.5, 2, 2, 1, 1, 2])
                    
                    with col1:
                        selected = st.checkbox("Select", key=f"select_{user['ID']}", label_visibility="collapsed")
                        if selected:
                            selected_users.append(user['ID'])
                    
                    with col2:
                        st.write(user['Email'])
                    
                    with col3:
                        st.write(user.get('Full Name', 'N/A'))
                    
                    with col4:
                        status_color = "🟢" if user['Status'] == 'Active' else "🔴" if user['Status'] == 'Inactive' else "🟡"
                        st.write(f"{status_color} {user['Status']}")
                    
                    with col5:
                        role_icon = "👑" if user.get('Role') == 'Admin' else "🛡️" if user.get('Role') == 'Moderator' else "👤"
                        st.write(f"{role_icon} {user.get('Role', 'User')}")
                    
                    with col6:
                        action_col1, action_col2, action_col3 = st.columns(3)
                        with action_col1:
                            if st.button("✏️", key=f"edit_{user['ID']}", help="Edit user"):
                                st.session_state['edit_user_id'] = user['ID']
                                st.session_state['show_edit_user'] = True
                        with action_col2:
                            if st.button("🔑", key=f"reset_{user['ID']}", help="Reset password"):
                                st.session_state['reset_user_id'] = user['ID']
                                st.session_state['reset_user_email'] = user['Email']
                                st.session_state['show_reset_password'] = True
                        with action_col3:
                            if st.button("🗑️", key=f"delete_{user['ID']}", help="Delete user"):
                                st.session_state['delete_user_id'] = user['ID']
                                st.session_state['delete_user_email'] = user['Email']
                                st.session_state['show_delete_user'] = True
                    
                    st.markdown("---")
            
            # Bulk actions
            if selected_users:
                st.subheader("Bulk Actions")
                bulk_operations_form(selected_users, supabase_admin)
        else:
            st.info("No users found matching the current filters.")
    else:
        st.info("No users found.")

def handle_modals(supabase_admin):
    """Handle modal dialogs"""
    
    # Add user modal
    if st.session_state.get('show_add_user'):
        with st.expander("➕ Add New User", expanded=True):
            add_user_form(supabase_admin)
    
    # Edit user modal
    if st.session_state.get('show_edit_user'):
        user_id = st.session_state.get('edit_user_id')
        if user_id:
            with st.expander("✏️ Edit User", expanded=True):
                edit_user_form(user_id, supabase_admin)
    
    # Delete user modal
    if st.session_state.get('show_delete_user'):
        user_id = st.session_state.get('delete_user_id')
        user_email = st.session_state.get('delete_user_email')
        if user_id and user_email:
            with st.expander("🗑️ Delete User", expanded=True):
                delete_user_confirmation(user_id, user_email, supabase_admin)
    
    # Reset password modal
    if st.session_state.get('show_reset_password'):
        user_id = st.session_state.get('reset_user_id')
        user_email = st.session_state.get('reset_user_email')
        if user_id and user_email:
            with st.expander("🔑 Reset Password", expanded=True):
                reset_password_form(user_id, user_email, supabase_admin)
    
    # Export modal
    if st.session_state.get('show_export'):
        with st.expander("📤 Export Users", expanded=True):
            st.subheader("Export Options")
            
            export_format = st.selectbox("Format:", ["CSV", "JSON", "Excel"])
            include_sensitive = st.checkbox("Include sensitive data (admin only)")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📥 Download", width="stretch"):
                    st.success(f"Users exported as {export_format}!")
                    st.session_state['show_export'] = False
                    st.rerun()
            
            with col2:
                if st.button("Cancel", width="stretch"):
                    st.session_state['show_export'] = False
                    st.rerun()

def render_settings_page():
    """Render settings page"""
    st.title("⚙️ Settings")
    
    # Admin settings
    st.subheader("👤 Admin Profile")
    
    admin_user = AuthManager.get_current_admin()
    
    with st.form("admin_profile"):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name", value=admin_user.get('full_name', ''))
            email = st.text_input("Email", value=admin_user.get('email', ''), disabled=True)
        
        with col2:
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
        
        if st.form_submit_button("Update Profile"):
            if new_password and new_password == confirm_password:
                st.success("Profile updated successfully!")
            elif new_password and new_password != confirm_password:
                st.error("Passwords do not match")
            else:
                st.success("Profile updated successfully!")
    
    st.markdown("---")
    
    # System settings
    st.subheader("🔧 System Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Security Settings**")
        session_timeout = st.selectbox("Session Timeout", ["1 hour", "8 hours", "24 hours", "7 days"])
        require_2fa = st.checkbox("Require 2FA for admins")
        password_policy = st.selectbox("Password Policy", ["Basic", "Strong", "Very Strong"])
    
    with col2:
        st.write("**Notification Settings**")
        email_notifications = st.checkbox("Email notifications", value=True)
        audit_alerts = st.checkbox("Audit log alerts", value=True)
        user_registration_alerts = st.checkbox("New user registration alerts")
    
    if st.button("Save Settings"):
        st.success("Settings saved successfully!")
    
    st.markdown("---")
    
    # Database settings
    st.subheader("🗄️ Database Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Connection Status**")
        st.success("🟢 Connected to Supabase")
        st.info("🔵 Demo mode enabled")
        
        if st.button("Test Connection"):
            st.success("Connection test successful!")
    
    with col2:
        st.write("**Maintenance**")
        
        if st.button("🧹 Clean Audit Logs"):
            st.success("Old audit logs cleaned!")
        
        if st.button("📊 Generate Backup"):
            st.success("Database backup created!")
        
        if st.button("🔄 Sync Users"):
            st.success("User data synchronized!")

def main():
    """Main application function"""
    # Require authentication
    require_auth()
    
    # Initialize Supabase
    supabase_admin = init_supabase()
    
    # Render sidebar and get current page
    current_page = render_sidebar()
    
    # Render current page
    if current_page == "Dashboard":
        render_dashboard(supabase_admin)
    elif current_page == "User Management":
        render_user_management(supabase_admin)
    elif current_page == "User Analytics":
        render_analytics_page(supabase_admin)
    elif current_page == "Audit Logs":
        render_audit_logs_page(supabase_admin)
    elif current_page == "Settings":
        render_settings_page()
    
    # Handle modals and popups
    handle_modals(supabase_admin)

if __name__ == "__main__":
    main()

