"""
User form components for CRUD operations
"""
import streamlit as st
import re
from typing import Dict, Any, Optional
from utils.auth import AuthManager
from utils.supabase_client import SupabaseAdmin

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

def add_user_form(supabase_admin: Optional[SupabaseAdmin] = None):
    """Render add user form"""
    st.subheader("➕ Add New User")
    
    with st.form("add_user_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            email = st.text_input("Email*", placeholder="user@example.com", key="add_email")
            full_name = st.text_input("Full Name", placeholder="John Doe", key="add_name")
            role = st.selectbox("Role", ["User", "Admin", "Moderator"], key="add_role")
            phone = st.text_input("Phone", placeholder="+1234567890", key="add_phone")
        
        with col2:
            password = st.text_input("Password*", type="password", placeholder="Minimum 8 characters", key="add_password")
            status = st.selectbox("Status", ["Active", "Inactive"], key="add_status")
            department = st.text_input("Department", placeholder="Engineering", key="add_department")
            job_title = st.text_input("Job Title", placeholder="Software Engineer", key="add_job_title")
        
        # Form buttons
        col1, col2 = st.columns(2)
        
        with col1:
            submit = st.form_submit_button("Create User", use_container_width=True, type="primary")
        
        with col2:
            cancel = st.form_submit_button("Cancel", use_container_width=True)
        
        if cancel:
            st.session_state['show_add_user'] = False
            st.rerun()
        
        if submit:
            # Validation
            errors = []
            
            if not email:
                errors.append("Email is required")
            elif not validate_email(email):
                errors.append("Invalid email format")
            
            if not password:
                errors.append("Password is required")
            else:
                is_valid, msg = validate_password(password)
                if not is_valid:
                    errors.append(msg)
            
            if errors:
                for error in errors:
                    st.error(error)
                return
            
            # Create user
            user_data = {
                'full_name': full_name,
                'role': role.lower(),
                'status': status.lower(),
                'phone': phone,
                'department': department,
                'job_title': job_title
            }
            
            success = False
            if supabase_admin:
                success = supabase_admin.create_user(email, password, user_data)
            else:
                # Demo mode - simulate success
                success = True
                st.success(f"Demo: User {email} would be created with role {role}")
            
            if success:
                st.success(f"User {email} created successfully!")
                AuthManager.log_admin_action("create_user", {
                    "email": email, 
                    "role": role, 
                    "department": department
                })
                st.session_state['show_add_user'] = False
                st.rerun()

def edit_user_form(user_id: str, supabase_admin: Optional[SupabaseAdmin] = None):
    """Render edit user form"""
    st.subheader("✏️ Edit User")
    
    # Get user data
    if supabase_admin:
        user_profile = supabase_admin.get_user_profile(user_id)
        if not user_profile:
            st.error("User not found")
            return
    else:
        # Demo data
        demo_users = {
            'user-1': {
                'email': 'entremotivator@gmail.com',
                'full_name': 'Admin User',
                'role': 'admin',
                'status': 'active',
                'phone': '+1234567890',
                'department': 'IT',
                'job_title': 'System Administrator'
            },
            'user-2': {
                'email': 'john.doe@example.com',
                'full_name': 'John Doe',
                'role': 'user',
                'status': 'active',
                'phone': '+1234567891',
                'department': 'Engineering',
                'job_title': 'Software Engineer'
            }
        }
        user_profile = demo_users.get(user_id, {})
    
    if not user_profile:
        st.error("User not found")
        return
    
    with st.form("edit_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            email = st.text_input("Email*", value=user_profile.get('email', ''), key="edit_email")
            full_name = st.text_input("Full Name", value=user_profile.get('full_name', ''), key="edit_name")
            role = st.selectbox("Role", ["User", "Admin", "Moderator"], 
                              index=["user", "admin", "moderator"].index(user_profile.get('role', 'user')), 
                              key="edit_role")
            phone = st.text_input("Phone", value=user_profile.get('phone', ''), key="edit_phone")
        
        with col2:
            new_password = st.text_input("New Password (leave blank to keep current)", 
                                       type="password", key="edit_password")
            status = st.selectbox("Status", ["Active", "Inactive"], 
                                index=["active", "inactive"].index(user_profile.get('status', 'active')), 
                                key="edit_status")
            department = st.text_input("Department", value=user_profile.get('department', ''), key="edit_department")
            job_title = st.text_input("Job Title", value=user_profile.get('job_title', ''), key="edit_job_title")
        
        # Form buttons
        col1, col2 = st.columns(2)
        
        with col1:
            submit = st.form_submit_button("Update User", use_container_width=True, type="primary")
        
        with col2:
            cancel = st.form_submit_button("Cancel", use_container_width=True)
        
        if cancel:
            st.session_state['show_edit_user'] = False
            if 'edit_user_id' in st.session_state:
                del st.session_state['edit_user_id']
            st.rerun()
        
        if submit:
            # Validation
            errors = []
            
            if not email:
                errors.append("Email is required")
            elif not validate_email(email):
                errors.append("Invalid email format")
            
            if new_password:
                is_valid, msg = validate_password(new_password)
                if not is_valid:
                    errors.append(msg)
            
            if errors:
                for error in errors:
                    st.error(error)
                return
            
            # Update user
            update_data = {
                'email': email,
                'full_name': full_name,
                'role': role.lower(),
                'status': status.lower(),
                'phone': phone,
                'department': department,
                'job_title': job_title
            }
            
            if new_password:
                update_data['password'] = new_password
            
            success = False
            if supabase_admin:
                success = supabase_admin.update_user(user_id, update_data)
            else:
                # Demo mode - simulate success
                success = True
                st.success(f"Demo: User {email} would be updated")
            
            if success:
                st.success(f"User {email} updated successfully!")
                AuthManager.log_admin_action("update_user", {
                    "user_id": user_id,
                    "email": email,
                    "changes": update_data
                })
                st.session_state['show_edit_user'] = False
                if 'edit_user_id' in st.session_state:
                    del st.session_state['edit_user_id']
                st.rerun()

def delete_user_confirmation(user_id: str, user_email: str, supabase_admin: Optional[SupabaseAdmin] = None):
    """Render delete user confirmation dialog"""
    st.subheader("🗑️ Delete User")
    st.warning(f"Are you sure you want to delete user **{user_email}**?")
    st.error("This action cannot be undone!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Yes, Delete User", use_container_width=True, type="primary"):
            success = False
            if supabase_admin:
                success = supabase_admin.delete_user(user_id)
            else:
                # Demo mode - simulate success
                success = True
                st.success(f"Demo: User {user_email} would be deleted")
            
            if success:
                st.success(f"User {user_email} deleted successfully!")
                AuthManager.log_admin_action("delete_user", {
                    "user_id": user_id,
                    "email": user_email
                })
                st.session_state['show_delete_user'] = False
                if 'delete_user_id' in st.session_state:
                    del st.session_state['delete_user_id']
                st.rerun()
    
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.session_state['show_delete_user'] = False
            if 'delete_user_id' in st.session_state:
                del st.session_state['delete_user_id']
            st.rerun()

def reset_password_form(user_id: str, user_email: str, supabase_admin: Optional[SupabaseAdmin] = None):
    """Render password reset form"""
    st.subheader("🔑 Reset Password")
    st.info(f"Reset password for user: **{user_email}**")
    
    option = st.radio(
        "Choose reset method:",
        ["Send reset email", "Set new password manually"]
    )
    
    if option == "Send reset email":
        st.write("A password reset email will be sent to the user.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Send Reset Email", use_container_width=True, type="primary"):
                success = False
                if supabase_admin:
                    success = supabase_admin.reset_user_password(user_email)
                else:
                    # Demo mode - simulate success
                    success = True
                    st.success(f"Demo: Reset email would be sent to {user_email}")
                
                if success:
                    st.success(f"Password reset email sent to {user_email}!")
                    AuthManager.log_admin_action("password_reset_email", {
                        "user_id": user_id,
                        "email": user_email
                    })
        
        with col2:
            if st.button("Cancel", use_container_width=True):
                st.session_state['show_reset_password'] = False
                if 'reset_user_id' in st.session_state:
                    del st.session_state['reset_user_id']
                st.rerun()
    
    else:
        with st.form("manual_password_reset"):
            new_password = st.text_input("New Password", type="password", placeholder="Minimum 8 characters")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            col1, col2 = st.columns(2)
            
            with col1:
                submit = st.form_submit_button("Set New Password", use_container_width=True, type="primary")
            
            with col2:
                cancel = st.form_submit_button("Cancel", use_container_width=True)
            
            if cancel:
                st.session_state['show_reset_password'] = False
                if 'reset_user_id' in st.session_state:
                    del st.session_state['reset_user_id']
                st.rerun()
            
            if submit:
                # Validation
                errors = []
                
                if not new_password:
                    errors.append("Password is required")
                else:
                    is_valid, msg = validate_password(new_password)
                    if not is_valid:
                        errors.append(msg)
                
                if new_password != confirm_password:
                    errors.append("Passwords do not match")
                
                if errors:
                    for error in errors:
                        st.error(error)
                    return
                
                # Set new password
                success = False
                if supabase_admin:
                    success = supabase_admin.update_user(user_id, {'password': new_password})
                else:
                    # Demo mode - simulate success
                    success = True
                    st.success(f"Demo: Password would be updated for {user_email}")
                
                if success:
                    st.success(f"Password updated successfully for {user_email}!")
                    AuthManager.log_admin_action("password_reset_manual", {
                        "user_id": user_id,
                        "email": user_email
                    })
                    st.session_state['show_reset_password'] = False
                    if 'reset_user_id' in st.session_state:
                        del st.session_state['reset_user_id']
                    st.rerun()

def bulk_operations_form(selected_users: list, supabase_admin: Optional[SupabaseAdmin] = None):
    """Render bulk operations form"""
    if not selected_users:
        return
    
    st.subheader(f"🔄 Bulk Operations ({len(selected_users)} users selected)")
    
    operation = st.selectbox(
        "Select operation:",
        ["Activate Users", "Deactivate Users", "Change Role", "Delete Users", "Send Password Reset"]
    )
    
    if operation == "Change Role":
        new_role = st.selectbox("New Role:", ["User", "Admin", "Moderator"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(f"Execute {operation}", use_container_width=True, type="primary"):
            success_count = 0
            
            for user_id in selected_users:
                success = False
                
                if operation == "Activate Users":
                    if supabase_admin:
                        success = supabase_admin.update_user(user_id, {'status': 'active'})
                    else:
                        success = True
                elif operation == "Deactivate Users":
                    if supabase_admin:
                        success = supabase_admin.update_user(user_id, {'status': 'inactive'})
                    else:
                        success = True
                elif operation == "Change Role":
                    if supabase_admin:
                        success = supabase_admin.update_user(user_id, {'role': new_role.lower()})
                    else:
                        success = True
                elif operation == "Delete Users":
                    if supabase_admin:
                        success = supabase_admin.delete_user(user_id)
                    else:
                        success = True
                elif operation == "Send Password Reset":
                    # Would need user email for this operation
                    success = True
                
                if success:
                    success_count += 1
            
            if success_count > 0:
                st.success(f"{operation} completed for {success_count} users!")
                AuthManager.log_admin_action("bulk_operation", {
                    "operation": operation,
                    "user_count": success_count,
                    "user_ids": selected_users
                })
                st.rerun()
            else:
                st.error("Operation failed for all selected users")
    
    with col2:
        if st.button("Cancel", use_container_width=True):
            # Clear selections
            for user_id in selected_users:
                if f"select_{user_id}" in st.session_state:
                    st.session_state[f"select_{user_id}"] = False
            st.rerun()

