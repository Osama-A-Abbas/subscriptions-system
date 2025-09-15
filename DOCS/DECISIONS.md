# DECISIONS.md

## Project Context

This project is a Django + DRF implementation of a Subscription Management Dashboard.  
Core goals: allow users to track subscriptions, get renewal reminders, and analyse costs.

---

## 1. Technology Choices

### Framework

- **Django 4.2 + Django REST Framework**  
  Chosen for rapid development, built-in admin, and well-documented ORM.  
  DRF simplifies building REST APIs for potential future frontend frameworks.

### Frontend

- **Django templates for now**  
  This allows me to deliver a working dashboard quickly with no heavy JS stack.  
  The API architecture allows swapping in React/Vue later if needed.

### Environment & Config

- `.env` with `django-environ` for SECRET_KEY, DEBUG, TIME_ZONE.  
  Keeps secrets out of source code and makes it easy to switch to production.

---

## 2. User Model Decision

- Using Django’s **default `User`** model.
- No custom phone/role fields because the assignment focuses on subscription management, not user management.
- Two user “types” handled via Django’s built-in `is_staff` / `is_superuser` flags.
- This avoids extra migration complexity and speeds up development.

---

## 3. Data Model Design

### Category

- `Category` model with self-relation `parent` to support nested categories/subcategories.
- Parent categories can be high-level groups (“Streaming”), subcategories can be specific services (“Netflix”).

### Subscription

- `Subscription` model linked to `User` with `ForeignKey`.
- Fields:
  - `monthly_cost` and `yearly_cost`: optional fields to store both billing cycles.
  - `billing_cycle`: indicates which plan the user currently pays.
  - `start_date`, `renewal_date`: track when subscription begins and next renewal.
  - `duration_months` and `duration_years`: duration-based fields replacing ending_date.
  - `is_active`: soft-delete indicator.
  - `auto_renewal`: boolean flag for automatic renewal.
  - `category`: optional link to `Category`.

### Duration-Based System

- **Replaced `ending_date` with duration fields** for more intuitive user experience.
- Users specify duration in months (for monthly billing) or years (for yearly billing).
- System automatically calculates ending date, total cost, and remaining payments.
- Decision: This approach is more user-friendly than requiring users to calculate end dates manually.

### Payment Tracking

- `Payment` model supports period-by-period tracking.
- `payment_date` allows null values for unpaid periods.
- `is_paid` defaults to False for new payment records.
- Decision (initial): Virtual payments created on-demand (no upfront future rows) to keep DB clean.
- Decision (revised 15 Sep 2025): When schedule changes (start date, billing cycle, duration), we reset payments by deleting all existing `Payment` rows for the subscription and letting the new schedule reflect fresh state. This avoids mismatches (e.g., switching monthly→yearly after paying months showing as fully paid years).

### Renewal Date

- Added a `calculate_next_renewal()` method to automatically compute the next renewal date based on `start_date` and `billing_cycle`.
- `save()` override sets `renewal_date` automatically if not provided.

### Cost Calculations

- Added `get_total_cost()` to compute total cost for entire subscription duration.
- Added `get_remaining_payments()` to track remaining payment periods.
- Added `get_billing_periods()` for virtual payment period generation.
- Decision: These methods provide comprehensive cost analysis and progress tracking.

---

## 4. UI/UX Design Decisions

### Form Design

- **Dynamic duration fields** that show/hide based on billing cycle selection.
- JavaScript-powered field toggling for better user experience.
- Smart form validation prevents mixing duration types (months vs years).
- Decision: This reduces user confusion and prevents data entry errors.

### Payment Management

- Period list shows Current (blue), Overdue Unpaid (red), Paid (green), Future Unpaid (default) with clear badges.
- Toggle actions: Mark as Paid / Mark as Unpaid per period.
- Confirmation pages when marking payments; consistent action texts/icons.
- Reusable components:
  - Boolean badge partial (`partials/badge_boolean.html`) used for Auto Renewal and Status.
  - Confirm modal partial (`partials/confirm_modal.html`) used on edit/save and can be reused elsewhere.
- Edit Subscription: When schedule-affecting fields change, show a confirm modal that warns “this will delete all payments and reset schedule”, then submit.
- Decision: On-demand creation of placeholders remains the default; after a reset we do not pre-create future rows.

### Admin Interface

- Enhanced admin with duration display and total cost calculations.
- Category seeder functionality for easy data population.
- Admin actions for bulk operations (e.g., seed categories).
- Decision: This improves admin efficiency and data management.

---

## 5. Code Architecture & Organization (16 Sep 2025)

### Layered Architecture Implementation

- **Models Package**: Refactored monolithic `models.py` (545 lines) into organized package structure:
  - `models/base.py`: Base models, mixins, and constants
  - `models/subscription.py`: Core Subscription model with mixin composition
  - `models/category.py`: Category model with mixins
  - `models/payment.py`: Payment model with mixins
  - `models/managers.py`: Custom managers and querysets
  - `models/mixins/`: Specialized mixins for different concerns:
    - `cost_calculations.py`: Cost and duration calculations
    - `payment_management.py`: Payment tracking and management
    - `renewal_logic.py`: Renewal dates and status logic
    - `schedule_management.py`: Billing periods and schedule management

### Service Layer Architecture

- **Services Package**: Created domain-specific services for business logic separation:
  - `services/payment_services.py`: Atomic payment operations
  - `services/subscription_services.py`: Subscription lifecycle management
  - `services/calculation_services.py`: Financial calculations and comparisons
  - `services/status_services.py`: Status determination and health monitoring
- **Decision**: Services handle write-side operations, keeping models focused on data representation

### View Layer Refactoring

- **Class-Based Views**: Converted all function-based views to CBVs for better maintainability:
  - `SubscriptionListView`, `SubscriptionDetailView`, `SubscriptionCreateView`
  - `SubscriptionUpdateView`, `SubscriptionDeleteView`, `PaymentActionView`
- **View Mixins**: Created reusable mixins for common functionality:
  - `UserOwnershipMixin`: Ensures users only access their own data
  - `LoggingMixin`: Consistent logging across views
  - `MessageMixin`: User messaging and feedback
  - `TransactionMixin`: Database transaction management
  - `ContextDataMixin`: Common context data
  - `ErrorHandlerMixin`: Consistent error handling

### Form Architecture Enhancement

- **Form Mixins**: Created specialized mixins for form functionality:
  - `BootstrapFormMixin`: Automatic Bootstrap styling
  - `CategoryOrderingMixin`: Smart category ordering
  - `CostValidationMixin`: Cost validation logic
  - `DurationValidationMixin`: Duration field validation
  - `FieldHelpTextMixin`: Dynamic help text
- **Form Utilities**: Created utility classes for form management:
  - `FormFieldFactory`: Dynamic field creation
  - `FormValidator`: Validation logic
  - `FormHelper`: Form manipulation utilities
  - `FormErrorHandler`: Error handling and display

### Template Component System

- **Reusable Partials**: Created modular template components:
  - `partials/form_field.html`: Standardized form field rendering
  - `partials/checkbox_field.html`: Checkbox field component
  - `partials/duration_fields.html`: Duration field group
  - `partials/form_actions.html`: Form action buttons
  - `partials/subscriptions_table.html`: Reusable subscription table
  - `partials/confirm_modal.html`: Bootstrap confirmation modals
- **Template Tags**: Created custom template filters:
  - `form_extras.py`: `add_class`, `add_attr` filters for dynamic styling

### JavaScript Architecture

- **Modular JavaScript**: Extracted inline JavaScript into organized modules:
  - `dashboard.js`: Dashboard functionality with robust content management
  - `subscription-forms.js`: Form behavior and validation
  - `utils.js`: General utility functions (toast notifications, formatting, etc.)
- **Error Handling**: Added comprehensive client-side error handling with try-catch blocks
- **Content Management**: Implemented robust content storage/restoration for dynamic UI

### Error Handling & Logging Infrastructure

- **Custom Exceptions**: Created domain-specific exception classes:
  - `SubscriptionError`, `PaymentError`, `ValidationError`
  - `BusinessLogicError`, `DataIntegrityError`, `ExternalServiceError`
- **Error Handlers**: Created decorators and mixins for consistent error handling:
  - `handle_errors` decorator for function-based views
  - `ErrorHandlerMixin` for class-based views
  - `log_operation` decorator for operation logging
- **Middleware**: Created custom middleware for global error handling:
  - `ErrorLoggingMiddleware`: Logs all unhandled exceptions
  - `RequestLoggingMiddleware`: Logs all requests for monitoring
- **Logging Configuration**: Comprehensive logging setup with multiple handlers:
  - File handlers for different log levels
  - Console handlers for development
  - Detailed formatters for debugging

### Selectors Pattern

- **Read-Only Queries**: Created `selectors.py` for read-only data access:
  - `get_user_subscriptions`: User-specific subscription queries
  - `compute_dashboard_totals`: Dashboard statistics calculation
- **Decision**: Separates read operations from write operations for better performance and clarity

### Management Commands

- **Debugging Tools**: Created management command for troubleshooting:
  - `debug_billing_periods.py`: Comprehensive billing period debugging
- **Existing Commands**: Maintained existing commands:
  - `update_subscriptions.py`: Subscription updates
  - `seed_categories.py`: Category seeding

### Settings & Configuration

- **Middleware Integration**: Added custom middleware to Django settings
- **Logging Configuration**: Comprehensive logging setup with file rotation
- **Environment Configuration**: Maintained environment-based configuration

---

## 6. Folder Structure

- **Refactored Structure**: Organized code into logical packages:
  ```
  subscriptions/
  ├── models/
  │   ├── __init__.py
  │   ├── base.py
  │   ├── subscription.py
  │   ├── category.py
  │   ├── payment.py
  │   ├── managers.py
  │   └── mixins/
  │       ├── __init__.py
  │       ├── cost_calculations.py
  │       ├── payment_management.py
  │       ├── renewal_logic.py
  │       └── schedule_management.py
  ├── services/
  │   ├── __init__.py
  │   ├── payment_services.py
  │   ├── subscription_services.py
  │   ├── calculation_services.py
  │   └── status_services.py
  ├── templates/partials/
  │   ├── form_field.html
  │   ├── checkbox_field.html
  │   ├── duration_fields.html
  │   ├── form_actions.html
  │   ├── subscriptions_table.html
  │   └── confirm_modal.html
  ├── static/js/
  │   ├── dashboard.js
  │   ├── subscription-forms.js
  │   └── utils.js
  ├── templatetags/
  │   ├── __init__.py
  │   └── form_extras.py
  ├── mixins.py
  ├── form_mixins.py
  ├── form_utils.py
  ├── selectors.py
  ├── error_handlers.py
  ├── exceptions.py
  ├── middleware.py
  └── views.py (refactored to CBVs)
  ```
- **Decision**: This structure promotes separation of concerns, reusability, and maintainability
