/**
 * Subscription Forms JavaScript Utilities
 *
 * Handles dynamic form behavior for subscription forms including:
 * - Duration field visibility based on billing cycle
 * - Form validation and confirmation modals
 * - Field clearing and state management
 */

class SubscriptionFormManager {
  constructor(formElement) {
    this.form = formElement;
    this.billingCycleSelect = null;
    this.durationMonthsField = null;
    this.durationYearsField = null;
    this.durationMonthsInput = null;
    this.durationYearsInput = null;

    this.init();
  }

  init() {
    this.findElements();
    this.setupEventListeners();
    this.initializeFieldVisibility();
  }

  findElements() {
    // Find billing cycle select
    this.billingCycleSelect = this.form.querySelector(
      'select[name="billing_cycle"]'
    );

    // Find duration field containers
    this.durationMonthsField = this.form.querySelector(
      "#duration-months-field"
    );
    this.durationYearsField = this.form.querySelector("#duration-years-field");

    // Find duration input fields
    this.durationMonthsInput = this.form.querySelector(
      'input[name="duration_months"]'
    );
    this.durationYearsInput = this.form.querySelector(
      'input[name="duration_years"]'
    );
  }

  setupEventListeners() {
    if (this.billingCycleSelect) {
      this.billingCycleSelect.addEventListener("change", () => {
        this.handleBillingCycleChange();
      });
    }
  }

  initializeFieldVisibility() {
    if (this.billingCycleSelect) {
      this.handleBillingCycleChange();
    }
  }

  handleBillingCycleChange() {
    const selectedValue = this.billingCycleSelect.value;

    switch (selectedValue) {
      case "monthly":
        this.showDurationMonths();
        this.clearDurationYears();
        break;
      case "yearly":
        this.showDurationYears();
        this.clearDurationMonths();
        break;
      default:
        this.hideAllDurationFields();
        break;
    }
  }

  showDurationMonths() {
    if (this.durationMonthsField) {
      this.durationMonthsField.style.display = "block";
    }
    if (this.durationYearsField) {
      this.durationYearsField.style.display = "none";
    }
  }

  showDurationYears() {
    if (this.durationYearsField) {
      this.durationYearsField.style.display = "block";
    }
    if (this.durationMonthsField) {
      this.durationMonthsField.style.display = "none";
    }
  }

  hideAllDurationFields() {
    if (this.durationMonthsField) {
      this.durationMonthsField.style.display = "none";
    }
    if (this.durationYearsField) {
      this.durationYearsField.style.display = "none";
    }
  }

  clearDurationMonths() {
    if (this.durationMonthsInput) {
      this.durationMonthsInput.value = "";
    }
  }

  clearDurationYears() {
    if (this.durationYearsInput) {
      this.durationYearsInput.value = "";
    }
  }
}

class ConfirmationModalManager {
  constructor(triggerElement, modalId) {
    this.trigger = triggerElement;
    this.modalId = modalId;
    this.modal = null;
    this.confirmBtn = null;

    this.init();
  }

  init() {
    this.findModalElements();
    this.setupEventListeners();
  }

  findModalElements() {
    if (this.modalId) {
      const modalElement = document.getElementById(this.modalId);
      if (modalElement) {
        this.modal = new bootstrap.Modal(modalElement);
        this.confirmBtn = modalElement.querySelector(
          `#${this.modalId}__confirmBtn`
        );
      }
    }
  }

  setupEventListeners() {
    if (this.trigger && this.modal && this.confirmBtn) {
      this.trigger.addEventListener("click", (e) => {
        e.preventDefault();
        this.modal.show();
      });

      this.confirmBtn.addEventListener("click", () => {
        this.modal.hide();
        this.submitForm();
      });
    }
  }

  submitForm() {
    if (this.trigger) {
      const form = this.trigger.closest("form");
      if (form) {
        form.submit();
      }
    }
  }
}

// Initialize forms when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  // Initialize subscription forms
  const subscriptionForms = document.querySelectorAll("form");
  subscriptionForms.forEach((form) => {
    // Check if this is a subscription form by looking for billing_cycle field
    const billingCycleField = form.querySelector(
      'select[name="billing_cycle"]'
    );
    if (billingCycleField) {
      new SubscriptionFormManager(form);
    }
  });

  // Initialize confirmation modals
  const confirmationTriggers = document.querySelectorAll(
    '[id*="confirmation-trigger"]'
  );
  confirmationTriggers.forEach((trigger) => {
    const modalId =
      trigger.getAttribute("data-modal-id") ||
      trigger.id.replace("-trigger", "");
    new ConfirmationModalManager(trigger, modalId);
  });
});

// Export for potential external use
window.SubscriptionFormManager = SubscriptionFormManager;
window.ConfirmationModalManager = ConfirmationModalManager;
