/**
 * Customizer — floating button + quiz modal that lets the student tweak
 * the layout without writing CSS. The answers are POSTed to /api/customize,
 * which Flask uses to write `static/css/customizations.css`. After a
 * successful submission the page reloads and the button is hidden on every
 * page (because the marker is now present in the CSS file).
 *
 * Built as an ES6 class to mirror the Gallery component's OOP style.
 */
class Customizer {
  constructor() {
    this.button = document.querySelector('.customizer-trigger');
    this.modal = document.querySelector('.customizer-modal');
    if (!this.button || !this.modal) return;

    this.form = this.modal.querySelector('form');
    this.closeBtn = this.modal.querySelector('.customizer-close');
    this.statusEl = this.modal.querySelector('.customizer-status');

    this.bindEvents();
  }

  bindEvents() {
    this.button.addEventListener('click', () => this.open());
    this.closeBtn?.addEventListener('click', () => this.close());
    this.modal.addEventListener('click', (event) => {
      if (event.target === this.modal) this.close();
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && this.isOpen()) this.close();
    });
    this.form?.addEventListener('submit', (event) => this.handleSubmit(event));
  }

  open() {
    this.modal.classList.add('is-open');
    this.modal.setAttribute('aria-hidden', 'false');
    this.modal.querySelector('input, button')?.focus();
    document.body.style.overflow = 'hidden';
  }

  close() {
    this.modal.classList.remove('is-open');
    this.modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  isOpen() {
    return this.modal.classList.contains('is-open');
  }

  /**
   * Collect form answers, send them to Flask, then reload the page so the
   * freshly written CSS is applied.
   * @param {SubmitEvent} event
   */
  async handleSubmit(event) {
    event.preventDefault();
    const formData = new FormData(this.form);
    const answers = Object.fromEntries(formData.entries());

    this.setStatus('Application en cours…');

    try {
      const response = await fetch('/api/customize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(answers),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      this.setStatus('Personnalisation enregistrée. Rechargement…');
      setTimeout(() => window.location.reload(), 600);
    } catch (error) {
      console.error('Customizer error:', error);
      this.setStatus('Une erreur est survenue. Réessaie.');
    }
  }

  setStatus(message) {
    if (this.statusEl) this.statusEl.textContent = message;
  }
}

document.addEventListener('DOMContentLoaded', () => new Customizer());
