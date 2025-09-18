"""
User Analytics Page
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

def render_analytics_page(supabase_admin=None):
    """Render user analytics page"""
    st.title("📈 User Analytics")
    
    # Time range selector
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        time_range = st.selectbox(
            "Time Range:",
            ["Last 7 days", "Last 30 days", "Last 90 days", "Last year", "All time"]
        )
    
    with col2:
        if st.button("🔄 Refresh Data", width="stretch"):
            st.cache_data.clear()
            st.rerun()
    
    with col3:
        if st.button("📊 Export Report", width="stretch"):
            st.success("Analytics report exported!")
    
    # Generate demo data
    def generate_demo_data():
        days = 30
        dates = [datetime.now() - timedelta(days=i) for i in range(days)]
        dates.reverse()
        
        # User registration data
        registrations = [random.randint(5, 25) for _ in range(days)]
        
        # Login activity data
        logins = [random.randint(50, 200) for _ in range(days)]
        
        # User engagement data
        active_users = [random.randint(100, 300) for _ in range(days)]
        
        return pd.DataFrame({
            'Date': dates,
            'New_Registrations': registrations,
            'Daily_Logins': logins,
            'Active_Users': active_users
        })
    
    df = generate_demo_data()
    
    # Key metrics
    st.subheader("📊 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_registrations = df['New_Registrations'].sum()
        st.metric(
            "New Registrations",
            total_registrations,
            delta=f"+{df['New_Registrations'].iloc[-1]} today"
        )
    
    with col2:
        avg_daily_logins = df['Daily_Logins'].mean()
        st.metric(
            "Avg Daily Logins",
            f"{avg_daily_logins:.0f}",
            delta=f"{((df['Daily_Logins'].iloc[-1] / avg_daily_logins - 1) * 100):+.1f}%"
        )
    
    with col3:
        avg_active_users = df['Active_Users'].mean()
        st.metric(
            "Avg Active Users",
            f"{avg_active_users:.0f}",
            delta=f"{((df['Active_Users'].iloc[-1] / avg_active_users - 1) * 100):+.1f}%"
        )
    
    with col4:
        engagement_rate = (df['Active_Users'].iloc[-1] / df['Daily_Logins'].iloc[-1]) * 100
        st.metric(
            "Engagement Rate",
            f"{engagement_rate:.1f}%",
            delta="+2.3%"
        )
    
    # Charts
    st.subheader("📈 Trends")
    
    # User registration trend
    fig_registrations = px.line(
        df, x='Date', y='New_Registrations',
        title='Daily User Registrations',
        color_discrete_sequence=['#00D4AA']
    )
    fig_registrations.update_layout(
        xaxis_title="Date",
        yaxis_title="New Registrations",
        showlegend=False
    )
    st.plotly_chart(fig_registrations, use_container_width=True)
    
    # Login activity
    col1, col2 = st.columns(2)
    
    with col1:
        fig_logins = px.bar(
            df.tail(14), x='Date', y='Daily_Logins',
            title='Daily Login Activity (Last 14 Days)',
            color_discrete_sequence=['#4ECDC4']
        )
        fig_logins.update_layout(showlegend=False)
        st.plotly_chart(fig_logins, use_container_width=True)
    
    with col2:
        fig_active = px.area(
            df.tail(14), x='Date', y='Active_Users',
            title='Active Users (Last 14 Days)',
            color_discrete_sequence=['#45B7D1']
        )
        fig_active.update_layout(showlegend=False)
        st.plotly_chart(fig_active, use_container_width=True)
    
    # User demographics
    st.subheader("👥 User Demographics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Department distribution
        dept_data = pd.DataFrame({
            'Department': ['Engineering', 'Marketing', 'Sales', 'HR', 'Finance', 'Operations'],
            'Count': [45, 23, 18, 12, 15, 20]
        })
        
        fig_dept = px.pie(
            dept_data, values='Count', names='Department',
            title='Users by Department'
        )
        st.plotly_chart(fig_dept, use_container_width=True)
    
    with col2:
        # Role distribution over time
        role_data = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'Admins': [3, 3, 4, 4, 5, 5],
            'Moderators': [8, 10, 12, 15, 18, 20],
            'Users': [120, 135, 150, 165, 180, 195]
        })
        
        fig_roles = go.Figure()
        fig_roles.add_trace(go.Scatter(x=role_data['Month'], y=role_data['Admins'], 
                                     mode='lines+markers', name='Admins'))
        fig_roles.add_trace(go.Scatter(x=role_data['Month'], y=role_data['Moderators'], 
                                     mode='lines+markers', name='Moderators'))
        fig_roles.add_trace(go.Scatter(x=role_data['Month'], y=role_data['Users'], 
                                     mode='lines+markers', name='Users'))
        
        fig_roles.update_layout(title='User Roles Growth', xaxis_title='Month', yaxis_title='Count')
        st.plotly_chart(fig_roles, use_container_width=True)
    
    # Activity heatmap
    st.subheader("🔥 Activity Heatmap")
    
    # Generate hourly activity data
    hours = list(range(24))
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    activity_data = []
    for day in days:
        for hour in hours:
            activity_data.append({
                'Day': day,
                'Hour': hour,
                'Activity': random.randint(10, 100)
            })
    
    activity_df = pd.DataFrame(activity_data)
    activity_pivot = activity_df.pivot(index='Day', columns='Hour', values='Activity')
    
    fig_heatmap = px.imshow(
        activity_pivot,
        title='User Activity Heatmap (by Hour and Day)',
        color_continuous_scale='Blues',
        aspect='auto'
    )
    fig_heatmap.update_layout(
        xaxis_title="Hour of Day",
        yaxis_title="Day of Week"
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Top users table
    st.subheader("🏆 Top Active Users")
    
    top_users_data = [
        {"User": "john.doe@example.com", "Logins": 156, "Last Active": "2 hours ago", "Department": "Engineering"},
        {"User": "jane.smith@example.com", "Logins": 142, "Last Active": "1 day ago", "Department": "Marketing"},
        {"User": "mike.wilson@example.com", "Logins": 138, "Last Active": "3 hours ago", "Department": "Sales"},
        {"User": "sarah.johnson@example.com", "Logins": 125, "Last Active": "5 hours ago", "Department": "HR"},
        {"User": "david.brown@example.com", "Logins": 118, "Last Active": "1 hour ago", "Department": "Finance"},
    ]
    
    top_users_df = pd.DataFrame(top_users_data)
    st.dataframe(top_users_df, use_container_width=True, hide_index=True)
    
    # Export options
    st.subheader("📤 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Charts", width="stretch"):
            st.success("Charts exported as PDF!")
    
    with col2:
        if st.button("📋 Export Data", width="stretch"):
            st.success("Data exported as CSV!")
    
    with col3:
        if st.button("📈 Generate Report", width="stretch"):
            st.success("Full analytics report generated!")

