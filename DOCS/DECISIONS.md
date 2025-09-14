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

- `Payment` model with virtual payment system for period-by-period tracking.
- Payment records created on-demand (not upfront) to maintain clean database.
- `payment_date` allows null values for unpaid periods.
- `is_paid` defaults to False for new payment records.
- Decision: Virtual payment system reduces database clutter while providing accurate tracking.

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

- **Virtual payment system** with period-by-period tracking.
- "Mark as Paid" buttons for individual billing periods.
- Confirmation pages for payment actions to prevent accidental changes.
- Status indicators (Current, Past Due, Paid) for clear visual feedback.
- Decision: This provides granular control while maintaining data integrity.

### Admin Interface

- Enhanced admin with duration display and total cost calculations.
- Category seeder functionality for easy data population.
- Admin actions for bulk operations (e.g., seed categories).
- Decision: This improves admin efficiency and data management.

---

## 5. Folder Structure

- Kept Django's default nested structure:
