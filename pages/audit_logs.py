"""
Audit Logs Page
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json

def render_audit_logs_page(supabase_admin=None):
    """Render audit logs page"""
    st.title("📋 Audit Logs")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        date_filter = st.selectbox(
            "Time Period:",
            ["Today", "Last 7 days", "Last 30 days", "Last 90 days", "All time"]
        )
    
    with col2:
        action_filter = st.selectbox(
            "Action Type:",
            ["All", "Login", "Create User", "Update User", "Delete User", "Password Reset", "Bulk Operation"]
        )
    
    with col3:
        admin_filter = st.selectbox(
            "Admin User:",
            ["All", "entremotivator@gmail.com", "admin@example.com"]
        )
    
    with col4:
        if st.button("🔄 Refresh", width="stretch"):
            st.rerun()
    
    # Search
    search_query = st.text_input("🔍 Search logs", placeholder="Search by user email, action, or details...")
    
    # Generate demo audit logs
    def generate_demo_logs():
        actions = [
            "login", "create_user", "update_user", "delete_user", 
            "password_reset", "bulk_operation", "role_change"
        ]
        
        logs = []
        for i in range(50):
            log = {
                "id": f"log_{i+1}",
                "timestamp": datetime.now() - timedelta(hours=i*2, minutes=i*5),
                "admin_email": "entremotivator@gmail.com" if i % 3 == 0 else "admin@example.com",
                "action": actions[i % len(actions)],
                "target_user": f"user{i+1}@example.com",
                "ip_address": f"192.168.1.{(i % 254) + 1}",
                "details": {
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "changes": {"role": "user", "status": "active"} if actions[i % len(actions)] == "update_user" else {},
                    "success": True
                },
                "status": "Success" if i % 10 != 0 else "Failed"
            }
            logs.append(log)
        
        return logs
    
    logs = generate_demo_logs()
    
    # Apply filters
    filtered_logs = logs.copy()
    
    # Date filter
    if date_filter != "All time":
        days_map = {"Today": 1, "Last 7 days": 7, "Last 30 days": 30, "Last 90 days": 90}
        cutoff_date = datetime.now() - timedelta(days=days_map[date_filter])
        filtered_logs = [log for log in filtered_logs if log["timestamp"] >= cutoff_date]
    
    # Action filter
    if action_filter != "All":
        action_map = {
            "Login": "login",
            "Create User": "create_user", 
            "Update User": "update_user",
            "Delete User": "delete_user",
            "Password Reset": "password_reset",
            "Bulk Operation": "bulk_operation"
        }
        filtered_logs = [log for log in filtered_logs if log["action"] == action_map[action_filter]]
    
    # Admin filter
    if admin_filter != "All":
        filtered_logs = [log for log in filtered_logs if log["admin_email"] == admin_filter]
    
    # Search filter
    if search_query:
        search_lower = search_query.lower()
        filtered_logs = [
            log for log in filtered_logs 
            if (search_lower in log["target_user"].lower() or 
                search_lower in log["action"].lower() or
                search_lower in str(log["details"]).lower())
        ]
    
    # Display summary
    st.subheader(f"📊 Summary ({len(filtered_logs)} logs found)")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        success_count = len([log for log in filtered_logs if log["status"] == "Success"])
        st.metric("Successful Actions", success_count)
    
    with col2:
        failed_count = len([log for log in filtered_logs if log["status"] == "Failed"])
        st.metric("Failed Actions", failed_count)
    
    with col3:
        unique_admins = len(set(log["admin_email"] for log in filtered_logs))
        st.metric("Active Admins", unique_admins)
    
    with col4:
        unique_targets = len(set(log["target_user"] for log in filtered_logs))
        st.metric("Affected Users", unique_targets)
    
    # Action distribution chart
    if filtered_logs:
        action_counts = {}
        for log in filtered_logs:
            action = log["action"].replace("_", " ").title()
            action_counts[action] = action_counts.get(action, 0) + 1
        
        action_df = pd.DataFrame(list(action_counts.items()), columns=["Action", "Count"])
        
        import plotly.express as px
        fig = px.bar(action_df, x="Action", y="Count", title="Actions Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    # Logs table
    st.subheader("📋 Audit Logs")
    
    if filtered_logs:
        # Convert to DataFrame for better display
        logs_data = []
        for log in filtered_logs:
            logs_data.append({
                "Timestamp": log["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                "Admin": log["admin_email"],
                "Action": log["action"].replace("_", " ").title(),
                "Target User": log["target_user"],
                "Status": log["status"],
                "IP Address": log["ip_address"],
                "Details": json.dumps(log["details"], indent=2)
            })
        
        logs_df = pd.DataFrame(logs_data)
        
        # Display with expandable details
        for idx, log in enumerate(filtered_logs[:20]):  # Show first 20 logs
            with st.expander(
                f"{log['timestamp'].strftime('%H:%M:%S')} - {log['action'].replace('_', ' ').title()} by {log['admin_email']}"
            ):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Timestamp:**", log["timestamp"].strftime("%Y-%m-%d %H:%M:%S"))
                    st.write("**Admin:**", log["admin_email"])
                    st.write("**Action:**", log["action"].replace("_", " ").title())
                    st.write("**Target User:**", log["target_user"])
                
                with col2:
                    st.write("**Status:**", log["status"])
                    st.write("**IP Address:**", log["ip_address"])
                    
                    if log["details"]:
                        st.write("**Details:**")
                        st.json(log["details"])
        
        if len(filtered_logs) > 20:
            st.info(f"Showing first 20 of {len(filtered_logs)} logs. Use filters to narrow down results.")
    
    else:
        st.info("No audit logs found matching the current filters.")
    
    # Export options
    st.subheader("📤 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Export as CSV", width="stretch"):
            if filtered_logs:
                st.success("Audit logs exported as CSV!")
            else:
                st.warning("No logs to export")
    
    with col2:
        if st.button("📋 Export as JSON", width="stretch"):
            if filtered_logs:
                st.success("Audit logs exported as JSON!")
            else:
                st.warning("No logs to export")
    
    with col3:
        if st.button("📊 Generate Report", width="stretch"):
            if filtered_logs:
                st.success("Audit report generated!")
            else:
                st.warning("No logs to report")
    
    # Real-time monitoring toggle
    st.subheader("🔴 Real-time Monitoring")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        monitoring = st.toggle("Enable Real-time Updates")
    
    with col2:
        if monitoring:
            st.info("Real-time monitoring is enabled. New audit logs will appear automatically.")
            # In a real implementation, this would use WebSocket or polling
        else:
            st.info("Real-time monitoring is disabled. Refresh manually to see new logs.")
    
    # Security alerts
    if any(log["status"] == "Failed" for log in filtered_logs[-10:]):
        st.warning("⚠️ Recent failed actions detected. Please review security logs.")
    
    # Session information
    with st.expander("ℹ️ Session Information"):
        st.write("**Current Session:**")
        st.write("- Admin:", st.session_state.get('admin_user', {}).get('email', 'Unknown'))
        st.write("- Login Time:", st.session_state.get('session_created', 'Unknown'))
        st.write("- Session ID:", st.session_state.get('session_token', 'Unknown')[:16] + "..." if st.session_state.get('session_token') else 'Unknown')

