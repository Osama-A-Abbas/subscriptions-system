/**
 * Dashboard JavaScript Utilities
 *
 * Handles dynamic dashboard functionality including:
 * - Quick action button interactions
 * - Content panel switching
 * - Dynamic content loading
 */

class DashboardManager {
  constructor() {
    this.actionsContainer = null;
    this.recentButton = null;
    this.compareButton = null;
    this.currentView = "recent";
    this.originalContent = null; // Store original content

    try {
      this.init();
    } catch (error) {
      console.error("Error initializing DashboardManager:", error);
      this.showError(
        "Failed to initialize dashboard. Please refresh the page."
      );
    }
  }

  init() {
    this.findElements();
    this.setupEventListeners();
    this.initializeDefaultView();
  }

  findElements() {
    this.actionsContainer = document.getElementById("actions-container");
    this.recentButton = document.getElementById("action-recent");
    this.compareButton = document.getElementById("action-compare");
  }

  setupEventListeners() {
    if (this.recentButton) {
      this.recentButton.addEventListener("click", () => {
        try {
          this.showRecentSubscriptions();
        } catch (error) {
          console.error("Error showing recent subscriptions:", error);
          this.showError("Failed to load recent subscriptions.");
        }
      });
    }

    if (this.compareButton) {
      this.compareButton.addEventListener("click", () => {
        try {
          this.showComparePlans();
        } catch (error) {
          console.error("Error showing compare plans:", error);
          this.showError("Failed to load compare plans.");
        }
      });
    }
  }

  initializeDefaultView() {
    // Default view is already set to recent subscriptions in the template
    this.currentView = "recent";
    this.updateButtonStates();

    // Store the original content for restoration with multiple attempts
    // to ensure all content is fully rendered
    this.attemptToStoreContent();
  }

  attemptToStoreContent(attempts = 0) {
    const maxAttempts = 5;
    const delay = 100 * (attempts + 1); // Increasing delay

    setTimeout(() => {
      if (this.storeOriginalContent()) {
        console.log(`Content stored successfully on attempt ${attempts + 1}`);
      } else if (attempts < maxAttempts - 1) {
        console.log(`Attempt ${attempts + 1} failed, trying again...`);
        this.attemptToStoreContent(attempts + 1);
      } else {
        console.warn("Failed to store content after all attempts");
      }
    }, delay);
  }

  showRecentSubscriptions() {
    if (this.currentView === "recent") return;

    this.currentView = "recent";
    this.updateButtonStates();
    this.loadRecentSubscriptions();
  }

  showComparePlans() {
    if (this.currentView === "compare") return;

    this.currentView = "compare";
    this.updateButtonStates();
    this.loadComparePlans();
  }

  updateButtonStates() {
    // Update recent button
    if (this.recentButton) {
      if (this.currentView === "recent") {
        this.recentButton.classList.remove("btn-outline-secondary");
        this.recentButton.classList.add("btn-secondary");
      } else {
        this.recentButton.classList.remove("btn-secondary");
        this.recentButton.classList.add("btn-outline-secondary");
      }
    }

    // Update compare button
    if (this.compareButton) {
      if (this.currentView === "compare") {
        this.compareButton.classList.remove("btn-outline-secondary");
        this.compareButton.classList.add("btn-secondary");
      } else {
        this.compareButton.classList.remove("btn-secondary");
        this.compareButton.classList.add("btn-outline-secondary");
      }
    }
  }

  storeOriginalContent(force = false) {
    // Store the original card body content
    const cardBody = this.actionsContainer?.querySelector(".card-body");
    if (cardBody && (!this.originalContent || force)) {
      this.originalContent = cardBody.innerHTML;
      console.log("Original content stored successfully");
      return true;
    } else if (!cardBody) {
      console.warn("Card body not found, cannot store original content");
      return false;
    } else if (this.originalContent && !force) {
      console.log("Original content already stored");
      return true;
    }
    return false;
  }

  loadRecentSubscriptions() {
    if (!this.actionsContainer) return;

    // Update the header
    const header = this.actionsContainer.querySelector(".card-header h5");
    if (header) {
      header.textContent = "Recent Subscriptions";
    }

    // Update the view more button
    const viewMoreBtn = this.actionsContainer.querySelector(
      ".btn-outline-primary"
    );
    if (viewMoreBtn) {
      viewMoreBtn.textContent = "View More";
    }

    // Restore the original content
    const cardBody = this.actionsContainer.querySelector(".card-body");
    if (cardBody) {
      if (this.originalContent) {
        cardBody.innerHTML = this.originalContent;
        console.log("Content restored from stored original");
      } else {
        // If no stored content, try to store it now
        console.log("No stored content found, storing current content");
        if (this.storeOriginalContent(true)) {
          console.log("Content stored and will be available for next switch");
        } else {
          console.error("Failed to store content");
        }
      }
    }
  }

  loadComparePlans() {
    if (!this.actionsContainer) return;

    // Ensure we have the original content stored before switching
    if (!this.originalContent) {
      this.storeOriginalContent(true);
    }

    // Update the header
    const header = this.actionsContainer.querySelector(".card-header h5");
    if (header) {
      header.textContent = "Compare Plans";
    }

    // Update the view more button
    const viewMoreBtn = this.actionsContainer.querySelector(
      ".btn-outline-primary"
    );
    if (viewMoreBtn) {
      viewMoreBtn.textContent = "View All Plans";
    }

    // The content would be loaded here
    // In a real application, you might fetch this via AJAX
    this.loadComparePlansContent();
  }

  loadComparePlansContent() {
    // This would typically load content via AJAX
    // For now, we'll just show a placeholder
    const cardBody = this.actionsContainer.querySelector(".card-body");
    if (cardBody) {
      cardBody.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-chart-line fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">Compare Plans</h5>
                    <p class="text-muted">Plan comparison content would be loaded here.</p>
                </div>
            `;
    }
  }

  showError(message) {
    // Show error message to user
    if (window.Utils && window.Utils.showToast) {
      window.Utils.showToast(message, "error");
    } else {
      alert(message);
    }
  }
}

// Initialize dashboard when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  try {
    // Only initialize if we're on the dashboard page
    if (document.querySelector("#actions-container")) {
      new DashboardManager();
    }
  } catch (error) {
    console.error("Error initializing dashboard:", error);
  }
});

// Export for potential external use
window.DashboardManager = DashboardManager;
