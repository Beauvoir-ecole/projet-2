/**
 * Gallery — filterable image grid.
 *
 * Built as an ES6 class for object-oriented design. Filters items by
 * category using a whitelist for defensive programming, and exposes
 * an accessible API (focus on the active button, ARIA pressed state).
 *
 * Usage: include this script at the bottom of the gallery page.
 */
class Gallery {
  /**
   * @param {Object} selectors
   * @param {string} selectors.gallery - CSS selector for the gallery grid container.
   * @param {string} selectors.filters - CSS selector for the filter buttons.
   */
  constructor(selectors) {
    this.gallery = document.querySelector(selectors.gallery);
    this.filterButtons = document.querySelectorAll(selectors.filters);

    if (!this.gallery || this.filterButtons.length === 0) {
      console.warn('Gallery: required DOM elements are missing.');
      return;
    }

    this.items = Array.from(this.gallery.querySelectorAll('.gallery-item'));
    this.allowedCategories = this.collectCategories();

    this.bindEvents();
  }

  /**
   * Build the whitelist of category values declared on items, plus "all".
   * @returns {Set<string>}
   */
  collectCategories() {
    const set = new Set(['all']);
    this.items.forEach((item) => {
      const category = item.dataset.category;
      if (category) set.add(category);
    });
    return set;
  }

  bindEvents() {
    this.filterButtons.forEach((button) => {
      button.addEventListener('click', () => this.filterBy(button.dataset.category));
    });
  }

  /**
   * Show items matching the given category, hide the rest.
   * Rejects values not present in the whitelist (defensive).
   * @param {string} category
   */
  filterBy(category) {
    if (!this.allowedCategories.has(category)) {
      console.warn(`Gallery: unknown category "${category}".`);
      return;
    }

    this.filterButtons.forEach((button) => {
      const active = button.dataset.category === category;
      button.classList.toggle('is-active', active);
      button.setAttribute('aria-pressed', String(active));
    });

    this.items.forEach((item) => {
      const match = category === 'all' || item.dataset.category === category;
      item.hidden = !match;
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new Gallery({
    gallery: '.gallery-grid',
    filters: '.filter-btn',
  });
});
