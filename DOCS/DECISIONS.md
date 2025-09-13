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
  - `is_active`: soft-delete indicator.
  - `category`: optional link to `Category`.

### Renewal Date
- Added a `calculate_next_renewal()` method to automatically compute the next renewal date based on `start_date` and `billing_cycle`.
- `save()` override sets `renewal_date` automatically if not provided.

### Savings Calculator
- Added `potential_savings()` to compute how much a user could save by switching billing cycle.
- The “other” cost field is optional; savings are calculated only when both costs are present.
- Decision: This reduces friction for the user — they can start with the cost of their current plan and optionally add the other cost later for more insights.

---

## 4. Folder Structure

- Kept Django’s default nested structure:
