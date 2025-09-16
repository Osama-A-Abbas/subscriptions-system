/**
 * Username Validation JavaScript
 *
 * Provides real-time username validation for better user experience.
 * Checks for uniqueness, format, and provides immediate feedback.
 */

class UsernameValidator {
  constructor() {
    this.reservedUsernames = [
      "admin",
      "administrator",
      "root",
      "user",
      "test",
      "api",
      "www",
      "mail",
      "support",
      "help",
      "info",
      "contact",
    ];
    this.minLength = 3;
    this.maxLength = 150;
    this.validPattern = /^[\w.@+-]+$/;
    this.debounceTimeout = null;
    this.debounceDelay = 500; // 500ms delay for API calls
  }

  init() {
    this.setupUsernameFields();
  }

  setupUsernameFields() {
    // Find all username input fields
    const usernameFields = document.querySelectorAll('input[name="username"]');

    usernameFields.forEach((field) => {
      this.attachValidation(field);
    });
  }

  attachValidation(field) {
    // Add event listeners
    field.addEventListener("input", (e) => {
      this.handleInput(e.target);
    });

    field.addEventListener("blur", (e) => {
      this.handleBlur(e.target);
    });

    // Add validation classes
    field.classList.add("username-field");
  }

  handleInput(field) {
    const username = field.value.trim();

    // Clear previous timeout
    if (this.debounceTimeout) {
      clearTimeout(this.debounceTimeout);
    }

    // Immediate validation for format
    const formatValidation = this.validateFormat(username);
    this.updateFieldState(field, formatValidation);

    // Debounced uniqueness check
    if (formatValidation.isValid && username.length >= this.minLength) {
      this.debounceTimeout = setTimeout(() => {
        this.checkUniqueness(field, username);
      }, this.debounceDelay);
    }
  }

  handleBlur(field) {
    const username = field.value.trim();
    const validation = this.validateFormat(username);

    if (validation.isValid && username.length >= this.minLength) {
      this.checkUniqueness(field, username);
    }
  }

  validateFormat(username) {
    const result = {
      isValid: true,
      message: "",
      type: "success",
    };

    // Check if empty
    if (!username) {
      result.isValid = false;
      result.message = "Username is required";
      result.type = "error";
      return result;
    }

    // Check minimum length
    if (username.length < this.minLength) {
      result.isValid = false;
      result.message = `Username must be at least ${this.minLength} characters long`;
      result.type = "error";
      return result;
    }

    // Check maximum length
    if (username.length > this.maxLength) {
      result.isValid = false;
      result.message = `Username must be ${this.maxLength} characters or fewer`;
      result.type = "error";
      return result;
    }

    // Check valid characters
    if (!this.validPattern.test(username)) {
      result.isValid = false;
      result.message =
        "Username can only contain letters, digits, and @/./+/-/_ characters";
      result.type = "error";
      return result;
    }

    // Check reserved usernames
    if (this.reservedUsernames.includes(username.toLowerCase())) {
      result.isValid = false;
      result.message =
        "This username is reserved. Please choose a different username";
      result.type = "error";
      return result;
    }

    // Check for common patterns that might be problematic
    if (username.startsWith(".") || username.endsWith(".")) {
      result.isValid = false;
      result.message = "Username cannot start or end with a dot";
      result.type = "error";
      return result;
    }

    if (username.includes("..")) {
      result.isValid = false;
      result.message = "Username cannot contain consecutive dots";
      result.type = "error";
      return result;
    }

    return result;
  }

  async checkUniqueness(field, username) {
    try {
      // Show loading state
      this.updateFieldState(field, {
        isValid: true,
        message: "Checking availability...",
        type: "info",
      });

      // Make API call to check uniqueness
      const response = await fetch("/api/check-username/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.getCSRFToken(),
        },
        body: JSON.stringify({
          username: username,
          current_user_id: this.getCurrentUserId(),
        }),
      });

      const data = await response.json();

      if (data.available) {
        this.updateFieldState(field, {
          isValid: true,
          message: "Username is available",
          type: "success",
        });
      } else {
        this.updateFieldState(field, {
          isValid: false,
          message: data.message || "This username is already taken",
          type: "error",
        });
      }
    } catch (error) {
      console.error("Error checking username uniqueness:", error);
      // Don't show error to user, just remove loading state
      this.updateFieldState(field, {
        isValid: true,
        message: "",
        type: "success",
      });
    }
  }

  updateFieldState(field, validation) {
    // Remove existing validation classes
    field.classList.remove("is-valid", "is-invalid");

    // Remove existing feedback
    const existingFeedback =
      field.parentNode.querySelector(".username-feedback");
    if (existingFeedback) {
      existingFeedback.remove();
    }

    // Add validation class
    if (validation.isValid) {
      field.classList.add("is-valid");
    } else {
      field.classList.add("is-invalid");
    }

    // Add feedback message
    if (validation.message) {
      const feedback = document.createElement("div");
      feedback.className = `username-feedback ${
        validation.type === "error" ? "invalid-feedback" : "valid-feedback"
      }`;
      feedback.textContent = validation.message;
      field.parentNode.appendChild(feedback);
    }
  }

  getCSRFToken() {
    const token = document.querySelector("[name=csrfmiddlewaretoken]");
    return token ? token.value : "";
  }

  getCurrentUserId() {
    // Try to get current user ID from a data attribute or global variable
    const userElement = document.querySelector("[data-user-id]");
    return userElement ? userElement.dataset.userId : null;
  }
}

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  const validator = new UsernameValidator();
  validator.init();
});

// Export for potential external use
window.UsernameValidator = UsernameValidator;
