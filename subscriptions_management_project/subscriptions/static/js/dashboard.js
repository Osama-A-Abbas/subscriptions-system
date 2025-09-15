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

    this.init();
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
        this.showRecentSubscriptions();
      });
    }

    if (this.compareButton) {
      this.compareButton.addEventListener("click", () => {
        this.showComparePlans();
      });
    }
  }

  initializeDefaultView() {
    // Default view is already set to recent subscriptions in the template
    this.currentView = "recent";
    this.updateButtonStates();
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

    // The content is already loaded in the template
    // In a real application, you might fetch this via AJAX
  }

  loadComparePlans() {
    if (!this.actionsContainer) return;

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
}

// Initialize dashboard when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  // Only initialize if we're on the dashboard page
  if (document.querySelector("#actions-container")) {
    new DashboardManager();
  }
});

// Export for potential external use
window.DashboardManager = DashboardManager;
