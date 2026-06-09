/**
 * ProgressNotifier — pedagogical helper visible in dev mode only.
 *
 * Fetches the next incomplete step from /api/progress, shows a floating
 * badge bottom-left, and displays a full-screen modal explaining what
 * the student should do next. When the student modifies the relevant
 * file and reloads the page, the next step appears automatically.
 */
class ProgressNotifier {
  constructor() {
    this.trigger = document.querySelector('.progress-trigger');
    this.modal = document.querySelector('.progress-modal');
    if (!this.trigger || !this.modal) return;

    this.badge = this.trigger.querySelector('[data-progress-badge]');
    this.closeBtn = this.modal.querySelector('.progress-close');
    this.countEl = this.modal.querySelector('[data-progress-count]');
    this.titleEl = this.modal.querySelector('[data-progress-title]');
    this.fileEl = this.modal.querySelector('[data-progress-file]');
    this.actionEl = this.modal.querySelector('[data-progress-action]');

    this.bindEvents();
    this.refresh();
  }

  bindEvents() {
    this.trigger.addEventListener('click', () => this.open());
    this.closeBtn?.addEventListener('click', () => this.close());
    this.modal.addEventListener('click', (event) => {
      if (event.target === this.modal) this.close();
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && this.isOpen()) this.close();
    });
  }

  async refresh() {
    try {
      const response = await fetch('/api/progress');
      if (!response.ok) return;
      const data = await response.json();
      if (data.done) {
        this.trigger.hidden = true;
        return;
      }
      this.render(data);
      this.trigger.hidden = false;
    } catch (error) {
      console.warn('ProgressNotifier:', error);
    }
  }

  render(step) {
    this.badge.textContent = step.index;
    this.countEl.textContent = `Étape ${step.index} sur ${step.total}`;
    this.titleEl.textContent = step.title;
    this.fileEl.textContent = step.file;
    this.actionEl.innerHTML = step.action;
  }

  open() {
    this.modal.classList.add('is-open');
    this.modal.setAttribute('aria-hidden', 'false');
    this.closeBtn?.focus();
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
}

document.addEventListener('DOMContentLoaded', () => new ProgressNotifier());
