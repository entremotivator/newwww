# 🚀 UserFlow Pro - Complete User Management Toolkit

A comprehensive Supabase-powered user management system built with Streamlit, featuring both admin dashboard and user portal interfaces.

## 🌟 Features

### 👤 User Portal
- **User Registration & Authentication**: Secure sign-up and login system
- **Profile Management**: Complete profile editing with personal information
- **Account Settings**: Notification preferences and privacy controls
- **Security Management**: Password changes and security overview
- **Preferences**: Theme, language, and timezone customization

### 🔐 Admin Dashboard
- **User Management**: Full CRUD operations for user accounts
- **Analytics & Reporting**: Comprehensive user analytics with charts
- **Audit Logs**: Complete activity tracking and monitoring
- **Bulk Operations**: Mass user management capabilities
- **Password Reset**: Admin-initiated password resets
- **Role Management**: User role assignment and permissions

### 🛠️ Database Features
- **Automated Setup**: One-click database schema creation
- **Row Level Security**: Comprehensive RLS policies
- **Audit Logging**: Automatic action tracking
- **User Sessions**: Session management and tracking
- **Preferences Storage**: User preference persistence

## 🏗️ Architecture

```
UserFlow Pro/
├── userflow_pro.py          # Main application entry point
├── enhanced_app.py           # Enhanced admin dashboard
├── utils/
│   ├── auth.py              # Admin authentication
│   ├── user_auth.py         # User authentication
│   ├── supabase_client.py   # Supabase client wrapper
│   └── database_setup.py    # Database setup utilities
├── components/
│   └── user_forms.py        # Reusable form components
├── pages/
│   ├── analytics.py         # Analytics dashboard
│   └── audit_logs.py        # Audit log viewer
├── database/
│   └── schema.sql           # Database schema
└── .streamlit/
    └── secrets.toml         # Configuration secrets
```

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+
- Supabase account and project
- Required Python packages (see requirements.txt)

### 2. Installation

```bash
# Clone or download the project
cd supabase-admin-app

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Update `.streamlit/secrets.toml` with your Supabase credentials:

```toml
[supabase]
url = "https://your-project.supabase.co"
key = "your-anon-key"
service_role_key = "your-service-role-key"

[admin]
default_email = "admin@example.com"
default_password = "your-admin-password"
```

### 4. Database Setup

1. Launch the application:
```bash
streamlit run userflow_pro.py
```

2. Click "Database Configuration & Setup"
3. Click "🔧 Run Database Setup" to create all necessary tables
4. Optionally click "👥 Create Sample Users" for demo data

### 5. Access the Applications

- **User Portal**: For regular users to manage their accounts
- **Admin Dashboard**: For administrators to manage all users

## 📊 Database Schema

### Core Tables

#### `profiles`
- User profile information
- Role and status management
- Contact details and metadata

#### `user_sessions`
- Active session tracking
- IP address and user agent logging
- Session expiration management

#### `audit_logs`
- Complete action tracking
- Admin activity monitoring
- Detailed change logging

#### `user_preferences`
- Theme and appearance settings
- Language and timezone preferences
- Notification preferences

#### `password_reset_tokens`
- Secure password reset workflow
- Token expiration and usage tracking

### Security Features

- **Row Level Security (RLS)**: All tables protected with comprehensive policies
- **Role-based Access**: Admin, moderator, and user roles
- **Audit Logging**: All admin actions automatically logged
- **Session Management**: Secure session handling and expiration
- **Password Security**: Encrypted password storage

## 🔧 Configuration Options

### App Settings
```toml
[app]
title = "UserFlow Pro - User Management Toolkit"
page_icon = "🚀"
layout = "wide"
```

### Email Configuration (Optional)
```toml
[email]
smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_username = "your-email@gmail.com"
smtp_password = "your-app-password"
```

## 🎯 Usage Examples

### Admin Operations

```python
# Initialize admin client
supabase_admin = SupabaseAdmin()

# Get all users
users = supabase_admin.get_all_users()

# Create new user
user_data = {
    'email': 'newuser@example.com',
    'password': 'securepassword',
    'full_name': 'New User'
}
supabase_admin.create_user(user_data)

# Update user role
supabase_admin.update_user_role(user_id, 'moderator')
```

### User Operations

```python
# Initialize user auth
user_auth = UserAuth()

# Sign up new user
user_auth.sign_up('user@example.com', 'password', 'Full Name')

# Update profile
profile_data = {
    'full_name': 'Updated Name',
    'job_title': 'Developer'
}
user_auth.update_user_profile(user_id, profile_data)
```

## 🔒 Security Best Practices

1. **Environment Variables**: Store sensitive credentials in environment variables
2. **RLS Policies**: All database access controlled by Row Level Security
3. **Session Management**: Automatic session expiration and validation
4. **Audit Logging**: All admin actions logged for compliance
5. **Password Policies**: Enforce strong password requirements

## 🚀 Deployment

### Streamlit Cloud
1. Push code to GitHub repository
2. Connect to Streamlit Cloud
3. Add secrets in Streamlit Cloud dashboard
4. Deploy application

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "userflow_pro.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 📈 Analytics Features

- **User Growth Tracking**: Registration and activity trends
- **Engagement Metrics**: Login frequency and session duration
- **Department Analytics**: User distribution by department
- **Activity Heatmaps**: Usage patterns by time and day
- **Export Capabilities**: CSV, JSON, and PDF reports

## 🔍 Audit & Compliance

- **Complete Action Logging**: Every admin action tracked
- **IP Address Tracking**: Security monitoring
- **Change History**: Detailed before/after comparisons
- **Export Capabilities**: Compliance reporting
- **Real-time Monitoring**: Live activity feeds

## 🛠️ Customization

### Adding New User Fields
1. Update database schema in `database_setup.py`
2. Modify profile forms in `components/user_forms.py`
3. Update user interface in `userflow_pro.py`

### Custom Analytics
1. Add new chart functions in `pages/analytics.py`
2. Create data aggregation queries
3. Implement export functionality

### Theme Customization
1. Update CSS in Streamlit configuration
2. Modify color schemes in chart configurations
3. Add custom styling options

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify Supabase credentials in secrets.toml
   - Check network connectivity
   - Ensure service role key has proper permissions

2. **Authentication Errors**
   - Verify RLS policies are properly configured
   - Check user roles and permissions
   - Ensure auth tables are properly set up

3. **Performance Issues**
   - Add database indexes for frequently queried columns
   - Implement pagination for large datasets
   - Use caching for expensive operations

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation for common solutions
- Review the troubleshooting section

## 🔄 Version History

### v1.0.0
- Initial release with complete user management
- Admin dashboard with analytics
- User portal with profile management
- Database setup automation
- Comprehensive audit logging

---

**UserFlow Pro** - Making user management simple, secure, and scalable! 🚀

