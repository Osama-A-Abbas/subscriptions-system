# 📊 Subscription Management System

A comprehensive Django-based web application for managing personal and business subscriptions with advanced payment tracking, cost analysis, and renewal management.

## 🎯 Project Overview

The Subscription Management System is designed to solve the common problem of tracking multiple subscriptions, their costs, renewal dates, and payment status. It provides users with a centralized dashboard to manage all their subscriptions efficiently, avoid missed payments, and analyze spending patterns.

### Key Problems Solved:

- **Subscription Overload**: Track unlimited subscriptions in one place
- **Payment Management**: Monitor payment status and avoid missed payments
- **Cost Analysis**: Analyze spending patterns and identify savings opportunities
- **Renewal Tracking**: Never miss a renewal with automated reminders
- **Financial Planning**: Plan budgets with accurate cost projections

## ✨ Features & Functionality

### 🔐 User Management

- **User Authentication**: Secure registration, login, and profile management
- **User Isolation**: Each user only sees their own subscriptions
- **Profile Management**: Update user information and preferences

### 📋 Subscription Management

- **CRUD Operations**: Create, read, update, and delete subscriptions
- **Flexible Billing**: Support for both monthly and yearly billing cycles
- **Duration-Based System**: Specify subscription duration in months or years
- **Category Organization**: Organize subscriptions with hierarchical categories
- **Auto-Renewal Tracking**: Monitor which subscriptions auto-renew

### 💰 Payment Tracking

- **Period-by-Period Tracking**: Track individual payment periods
- **Payment Status**: Mark payments as paid/unpaid with visual indicators
- **Current Period Detection**: Automatically identify current billing periods
- **Payment History**: View complete payment history for each subscription
- **Overdue Detection**: Identify and highlight overdue payments

### 📊 Dashboard & Analytics

- **Overview Dashboard**: Quick access to subscription summary and statistics
- **Recent Subscriptions**: View latest subscriptions with quick actions
- **Cost Analysis**: Total monthly/yearly spending calculations
- **Payment Progress**: Visual progress indicators for subscription payments
- **Quick Actions**: Fast access to common operations

### 🎨 User Interface

- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Bootstrap UI**: Modern, clean interface with consistent styling
- **Dynamic Forms**: Smart form fields that adapt based on user input
- **Interactive Elements**: Confirmation modals and dynamic content switching
- **Visual Indicators**: Color-coded status indicators for easy recognition

### 🔧 Advanced Features

- **Schedule Management**: Automatic billing period generation
- **Cost Calculations**: Comprehensive financial calculations and projections
- **Plan Comparison**: Compare different billing cycles for cost savings
- **Error Handling**: Robust error handling with user-friendly messages
- **Logging System**: Comprehensive logging for debugging and monitoring

## 🛠 Technical Stack

### Backend

- **Django 4.2**: Web framework with built-in admin and ORM
- **Django REST Framework**: API framework for future frontend integration
- **Python 3.13**: Programming language
- **SQLite**: Database (easily configurable for PostgreSQL/MySQL)

### Frontend

- **Django Templates**: Server-side rendering with template inheritance
- **Bootstrap 5**: CSS framework for responsive design
- **JavaScript (ES6+)**: Client-side interactivity and form handling
- **Font Awesome**: Icon library for consistent UI elements

### Development Tools

- **django-environ**: Environment variable management
- **python-dateutil**: Advanced date manipulation
- **django-crontab**: Task scheduling for automated processes

### Architecture

- **Layered Architecture**: Models, Services, Views, Templates separation
- **Mixin Pattern**: Reusable functionality across models and views
- **Service Layer**: Business logic separation from views
- **Class-Based Views**: Modern Django view patterns
- **Custom Managers**: Enhanced database query capabilities

## 🚀 Installation & Setup

### Prerequisites

- Python 3.13 or higher
- pip (Python package installer)
- Git (for cloning the repository)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd subscriptions-system
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
TIME_ZONE=UTC
```

### Step 5: Database Setup

```bash
# Navigate to project directory
cd subscriptions_management_project

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### Step 6: Seed Categories (Optional)

```bash
python manage.py seed_categories
```

### Step 7: Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## 📖 Usage & Quick Start

### 1. User Registration

- Navigate to the application URL
- Click "Register" to create a new account
- Fill in your details and create an account

### 2. Adding Subscriptions

- Click "Add New Subscription" from the dashboard
- Fill in subscription details:
  - **Name**: Service name (e.g., "Netflix")
  - **Costs**: Monthly and/or yearly costs
  - **Billing Cycle**: Choose monthly or yearly
  - **Duration**: How long the subscription lasts
  - **Start Date**: When the subscription begins
  - **Category**: Organize by category
- Click "Add Subscription"

### 3. Managing Payments

- View subscription details to see billing periods
- Click "Mark as Paid" for completed payments
- Use "Mark as Unpaid" to reverse payment status
- View payment progress and overdue indicators

### 4. Dashboard Features

- **Recent Subscriptions**: View your latest 5 subscriptions
- **Quick Actions**: Fast access to common operations
- **Cost Summary**: See total monthly/yearly spending
- **Payment Status**: Overview of payment progress

### 5. Admin Interface

- Access admin at `/admin/` (requires superuser account)
- Manage subscriptions, categories, and users
- View system statistics and perform bulk operations

## 🔗 API Endpoints

The application is built with Django REST Framework for future API expansion:

### Authentication Endpoints

- `POST /accounts/register/` - User registration
- `POST /accounts/login/` - User login
- `POST /accounts/logout/` - User logout

### Subscription Endpoints

- `GET /subscriptions/` - List user subscriptions
- `POST /subscriptions/add/` - Create new subscription
- `GET /subscriptions/{id}/` - Get subscription details
- `PUT /subscriptions/{id}/edit/` - Update subscription
- `DELETE /subscriptions/{id}/delete/` - Delete subscription

### Payment Endpoints

- `POST /subscriptions/{id}/payment/` - Add payment record
- `POST /subscriptions/{id}/mark-paid/{period}/` - Mark payment as paid
- `POST /subscriptions/{id}/mark-unpaid/{period}/` - Mark payment as unpaid

## 🏗 Directory Structure & Architecture

```
subscriptions-system/
├── DOCS/                           # Project documentation
│   ├── DECISIONS.md               # Architectural decisions
│   ├── TasksProgression.md        # Development progress
│   └── Commands.md                # Management commands
├── subscriptions_management_project/
│   ├── subscriptions/             # Main application
│   │   ├── models/               # Data models (refactored)
│   │   │   ├── __init__.py
│   │   │   ├── base.py           # Base models and mixins
│   │   │   ├── subscription.py   # Subscription model
│   │   │   ├── category.py       # Category model
│   │   │   ├── payment.py        # Payment model
│   │   │   ├── managers.py       # Custom managers
│   │   │   └── mixins/           # Model mixins
│   │   │       ├── cost_calculations.py
│   │   │       ├── payment_management.py
│   │   │       ├── renewal_logic.py
│   │   │       └── schedule_management.py
│   │   ├── services/             # Business logic services
│   │   │   ├── payment_services.py
│   │   │   ├── subscription_services.py
│   │   │   ├── calculation_services.py
│   │   │   └── status_services.py
│   │   ├── templates/            # Django templates
│   │   │   ├── subscriptions/    # Subscription templates
│   │   │   └── partials/         # Reusable components
│   │   ├── static/js/            # JavaScript modules
│   │   │   ├── dashboard.js      # Dashboard functionality
│   │   │   ├── subscription-forms.js
│   │   │   └── utils.js          # Utility functions
│   │   ├── templatetags/         # Custom template tags
│   │   ├── management/commands/  # Django management commands
│   │   ├── mixins.py             # View mixins
│   │   ├── form_mixins.py        # Form mixins
│   │   ├── form_utils.py         # Form utilities
│   │   ├── selectors.py          # Read-only queries
│   │   ├── error_handlers.py     # Error handling
│   │   ├── exceptions.py         # Custom exceptions
│   │   ├── middleware.py         # Custom middleware
│   │   ├── views.py              # Class-based views
│   │   ├── forms.py              # Django forms
│   │   ├── urls.py               # URL patterns
│   │   └── admin.py              # Admin configuration
│   ├── accounts/                 # User authentication app
│   ├── subscriptions_management_project/  # Project settings
│   │   ├── settings.py           # Django settings
│   │   ├── urls.py               # Main URL configuration
│   │   └── wsgi.py               # WSGI configuration
│   └── manage.py                 # Django management script
├── venv/                         # Virtual environment
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

### Architecture Patterns

#### 1. **Layered Architecture**

- **Models Layer**: Data representation with mixins for functionality
- **Services Layer**: Business logic and complex operations
- **Views Layer**: Request handling with reusable mixins
- **Templates Layer**: UI presentation with reusable components

#### 2. **Mixin Pattern**

- **Model Mixins**: Reusable functionality across models
- **View Mixins**: Common view behavior (logging, error handling, etc.)
- **Form Mixins**: Reusable form functionality

#### 3. **Service Layer Pattern**

- **Payment Services**: Payment-related operations
- **Subscription Services**: Subscription lifecycle management
- **Calculation Services**: Financial calculations
- **Status Services**: Status determination and health checks

## 🛠 Management Commands

### Available Commands

#### 1. **Seed Categories**

```bash
python manage.py seed_categories
```

Populates the database with default subscription categories and subcategories.

#### 2. **Debug Billing Periods**

```bash
python manage.py debug_billing_periods <subscription_id>
```

Debug billing period generation and current period detection for a specific subscription.

#### 3. **Update Subscriptions**

```bash
python manage.py update_subscriptions
```

Updates subscription renewal dates and processes scheduled tasks.

### Custom Commands Usage

```bash
# List all available commands
python manage.py help

# Get help for specific command
python manage.py help <command_name>
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test subscriptions

# Run tests with coverage
coverage run --source='.' manage.py test
coverage report
```

## 🚀 Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Configure proper database (PostgreSQL recommended)
- [ ] Set up static file serving
- [ ] Configure email settings for notifications
- [ ] Set up logging and monitoring
- [ ] Configure HTTPS/SSL
- [ ] Set up backup procedures

### Environment Variables

```env
SECRET_KEY=your-production-secret-key
DJANGO_DEBUG=False
DATABASE_URL=postgresql://user:password@host:port/dbname
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## 🤝 Contributing Guidelines

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes
4. Add tests for new functionality
5. Run tests: `python manage.py test`
6. Commit changes: `git commit -m 'Add new feature'`
7. Push to branch: `git push origin feature/new-feature`
8. Submit a pull request

### Code Standards

- Follow PEP 8 Python style guide
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Write tests for new functionality
- Update documentation for new features

### Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Add clear description of changes
4. Reference any related issues
5. Request review from maintainers

## 📝 License

None

## 🆘 Support & Troubleshooting

### Common Issues

#### 1. **Database Migration Errors**

```bash
# Reset migrations (development only)
python manage.py migrate --fake-initial
```

#### 2. **Static Files Not Loading**

```bash
# Collect static files
python manage.py collectstatic
```

#### 3. **Permission Errors**

```bash
# Fix file permissions
chmod +x manage.py
```

### Getting Help

- Review the documentation in the `DOCS/` folder
- Contact Me on osamaabbaswo@gmail.com

## 🔮 Future Enhancements

### Planned Features

- **Real Subscription Services API Integration**: Integration with real subs-services provider.  
- **Email Notifications**: Automated renewal reminders
- **Advance Cost Analytics**: Advanced spending analysis and reports
- **Export Functionality**: Export data to CSV/PDF
- **Multi-Currency Support**: Support for different currencies
- **Team Management**: Shared subscription management
- **Mobile App**: Native mobile application
- **Integration APIs**: Connect with bank accounts and actual payment services

### Technical Improvements

- **Performance Optimization**: Database query optimization
- **Caching**: Redis integration for better performance
- **Background Tasks**: Celery integration for async processing
- **Monitoring**: Application performance monitoring
- **Security**: Enhanced security features and audit logging

---

**Built with ❤️ By Osama-A-Abbas using Django and modern web technologies**
