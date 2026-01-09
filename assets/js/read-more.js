// Read More Toggle Functionality
// Reusable module that works with data-read-more attribute
// Supports progressive enhancement - works without JavaScript

(function() {
  'use strict';

  // Add js-enabled class to document when JavaScript is available
  document.documentElement.classList.add('js-enabled');

  function initReadMore() {
    // Find all elements with data-read-more attribute
    const readMoreContainers = document.querySelectorAll('[data-read-more]');

    readMoreContainers.forEach(function(container) {
      // Skip if already initialized
      if (container.classList.contains('read-more-initialized')) {
        return;
      }

      // Mark as initialized
      container.classList.add('read-more-initialized');

      // Get button text from data attributes or use defaults
      const readMoreText = container.getAttribute('data-read-more') || 'Read more';
      const readLessText = container.getAttribute('data-read-less') || 'Show less';

      // Add class to container for CSS targeting
      container.classList.add('read-more-content');

      // Create toggle button
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'read-more-toggle';
      button.textContent = readMoreText;
      button.setAttribute('aria-expanded', 'false');
      button.setAttribute('aria-controls', container.id || 'read-more-' + Math.random().toString(36).substr(2, 9));

      // Set container ID if it doesn't have one
      if (!container.id) {
        container.id = button.getAttribute('aria-controls');
      }

      // Insert button before the container
      container.parentNode.insertBefore(button, container);

      // Track expanded state
      let isExpanded = false;

      // Toggle function
      function toggleContent() {
        isExpanded = !isExpanded;

        if (isExpanded) {
          container.classList.add('read-more-expanded');
          container.classList.remove('read-more-collapsed');
          button.textContent = readLessText;
          button.setAttribute('aria-expanded', 'true');
        } else {
          container.classList.remove('read-more-expanded');
          container.classList.add('read-more-collapsed');
          button.textContent = readMoreText;
          button.setAttribute('aria-expanded', 'false');
        }
      }

      // Add click event listener
      button.addEventListener('click', toggleContent);

      // Support keyboard navigation (Enter and Space)
      button.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          toggleContent();
        }
      });

      // Initialize as collapsed
      container.classList.add('read-more-collapsed');
    });
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initReadMore);
  } else {
    // DOM is already ready
    initReadMore();
  }
})();










