/**
 * Poetry typewriter modal functionality
 * Opens modal with typewriter animation when clicking poems in creative grid
 */

(function() {
  'use strict';

  // Typewriter animation function
  function typeWriter(element, text, speed, callback) {
    let i = 0;
    const textArray = text.split('');
    const isSkipped = { value: false };
    
    function type() {
      if (i < textArray.length && !isSkipped.value) {
        element.textContent += textArray[i];
        i++;
        setTimeout(type, speed);
      } else if (callback && !isSkipped.value) {
        callback();
      }
    }
    
    // Allow skipping animation by clicking
    element.addEventListener('click', function skipAnimation() {
      if (i < textArray.length) {
        isSkipped.value = true;
        element.textContent = text;
        element.removeEventListener('click', skipAnimation);
        if (callback) {
          callback();
        }
      }
    }, { once: true });
    
    type();
  }

  // Create poetry modal
  function createPoetryModal() {
    if (document.getElementById('poetryModal')) {
      return; // Modal already exists
    }
    
    const modal = document.createElement('div');
    modal.id = 'poetryModal';
    modal.className = 'poetry-modal';
    modal.innerHTML = `
      <div class="poetry-modal-content">
        <span class="poetry-modal-close">&times;</span>
        <div class="poetry-modal-header">
          <h2 class="poetry-modal-title"></h2>
        </div>
        <div class="poetry-modal-body">
          <div class="poetry-text-container">
            <div class="poetry-text"></div>
          </div>
        </div>
        <div class="poetry-modal-footer">
          <div class="poetry-modal-nav">
            <button class="poetry-nav-btn poetry-prev" aria-label="Previous poem" style="display: none;">
              <i class="fas fa-chevron-left"></i> Previous
            </button>
            <button class="poetry-nav-btn poetry-next" aria-label="Next poem" style="display: none;">
              Next <i class="fas fa-chevron-right"></i>
            </button>
          </div>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
    
    // Close modal handlers
    const closeBtn = modal.querySelector('.poetry-modal-close');
    closeBtn.addEventListener('click', closePoetryModal);
    
    modal.addEventListener('click', function(event) {
      if (event.target === modal) {
        closePoetryModal();
      }
    });
    
    // Keyboard close (ESC)
    document.addEventListener('keydown', function handleKeydown(e) {
      if (e.key === 'Escape' && modal.style.display === 'block') {
        closePoetryModal();
        document.removeEventListener('keydown', handleKeydown);
      }
    });
  }

  // Close poetry modal
  function closePoetryModal() {
    const modal = document.getElementById('poetryModal');
    if (modal) {
      modal.style.display = 'none';
      const textContainer = modal.querySelector('.poetry-text');
      if (textContainer) {
        textContainer.textContent = '';
      }
    }
  }

  // Open poetry modal with typewriter effect
  window.openPoetryModal = function(poemTitle, poemContent, poemUrl, poemIndex, allPoems) {
    createPoetryModal();
    
    const modal = document.getElementById('poetryModal');
    const titleEl = modal.querySelector('.poetry-modal-title');
    const textEl = modal.querySelector('.poetry-text');
    const prevBtn = modal.querySelector('.poetry-prev');
    const nextBtn = modal.querySelector('.poetry-next');
    
    // Set title
    titleEl.textContent = poemTitle || 'Poem';
    
    // Clear previous content
    textEl.textContent = '';
    
    // Show modal
    modal.style.display = 'block';
    
    // Show/hide navigation buttons
    if (allPoems && allPoems.length > 1) {
      prevBtn.style.display = poemIndex > 0 ? 'inline-block' : 'none';
      nextBtn.style.display = poemIndex < allPoems.length - 1 ? 'inline-block' : 'none';
      
      // Navigation handlers
      prevBtn.onclick = function() {
        if (poemIndex > 0) {
          const prevPoem = allPoems[poemIndex - 1];
          // Fetch content if not already loaded
          if (prevPoem.content) {
            openPoetryModal(prevPoem.title, prevPoem.content, prevPoem.url, poemIndex - 1, allPoems);
          } else {
            fetchPoemContent(prevPoem, poemIndex - 1, allPoems);
          }
        }
      };
      
      nextBtn.onclick = function() {
        if (poemIndex < allPoems.length - 1) {
          const nextPoem = allPoems[poemIndex + 1];
          // Fetch content if not already loaded
          if (nextPoem.content) {
            openPoetryModal(nextPoem.title, nextPoem.content, nextPoem.url, poemIndex + 1, allPoems);
          } else {
            fetchPoemContent(nextPoem, poemIndex + 1, allPoems);
          }
        }
      };
    } else {
      prevBtn.style.display = 'none';
      nextBtn.style.display = 'none';
    }
    
    // Typewriter animation
    // Speed: ~50 characters per second (adjustable)
    const typingSpeed = 20; // milliseconds per character
    typeWriter(textEl, poemContent, typingSpeed, function() {
      // Animation complete
      textEl.style.cursor = 'default';
    });
    
    // Add click hint initially
    textEl.style.cursor = 'pointer';
    textEl.title = 'Click to reveal all text';
  };

  // Helper function to fetch poem content
  function fetchPoemContent(poem, poemIndex, allPoems) {
    if (!poem || !poem.url) {
      console.warn('Cannot fetch poem: missing URL');
      return;
    }
    
    fetch(poem.url)
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to fetch poem');
        }
        return response.text();
      })
      .then(html => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const contentEl = doc.querySelector('article, .post, main, .content');
        let poemContent = '';
        
        if (contentEl) {
          const contentClone = contentEl.cloneNode(true);
          const elementsToRemove = contentClone.querySelectorAll('h1, .post-title, .post-header, header, .card-body, .card-title, nav, footer, script, style');
          elementsToRemove.forEach(el => el.remove());
          
          const paragraphs = contentClone.querySelectorAll('p');
          const preElements = contentClone.querySelectorAll('pre');
          
          if (preElements.length > 0) {
            poemContent = Array.from(preElements)
              .map(pre => pre.textContent.trim())
              .join('\n\n');
          } else if (paragraphs.length > 0) {
            poemContent = Array.from(paragraphs)
              .map(p => {
                const pClone = p.cloneNode(true);
                const brs = pClone.querySelectorAll('br');
                brs.forEach(br => br.replaceWith('\n'));
                return pClone.textContent.trim();
              })
              .filter(text => text.length > 0)
              .join('\n\n');
          } else {
            let text = contentClone.textContent.trim();
            text = text.replace(/\n{3,}/g, '\n\n');
            poemContent = text;
          }
        }
        
        if (!poemContent) {
          console.warn('Could not extract poem content from:', poem.url);
          // Fallback: open page normally
          if (poem.url) {
            window.location.href = poem.url;
          }
          return;
        }
        
        // Store content for future use
        if (poem) {
          poem.content = poemContent;
        }
        openPoetryModal(poem.title, poemContent, poem.url, poemIndex, allPoems);
      })
      .catch(error => {
        console.error('Error fetching poem:', error);
        // Fallback: try to open the page normally
        if (poem && poem.url) {
          window.location.href = poem.url;
        }
      });
  }

  // Initialize poem click handlers on page load
  window.addEventListener('load', function() {
    // Find all poem cards in creative grid
    const poemCards = document.querySelectorAll('[data-category="poems"]');
    
    poemCards.forEach(function(card, index) {
      // Get poem data from card
      const titleEl = card.querySelector('.card-title, h2, h3');
      const title = titleEl ? titleEl.textContent.trim() : '';
      const linkEl = card.querySelector('a[href]');
      const poemUrl = linkEl ? linkEl.getAttribute('href') : '';
      
      // Make card clickable
      card.style.cursor = 'pointer';
      
      // Add click handler
      card.addEventListener('click', function(e) {
        // Don't trigger if clicking on a link
        if (e.target.tagName === 'A' || e.target.closest('a')) {
          return;
        }
        
        e.preventDefault();
        e.stopPropagation();
        
        // Collect all poems in same series for navigation
        const allPoems = [];
        const seriesGroup = card.closest('.row, .container');
        if (seriesGroup) {
          const allCards = seriesGroup.querySelectorAll('[data-category="poems"]');
          allCards.forEach(function(otherCard, idx) {
            const otherTitleEl = otherCard.querySelector('.card-title, h2, h3');
            const otherTitle = otherTitleEl ? otherTitleEl.textContent.trim() : '';
            const otherLinkEl = otherCard.querySelector('a[href]');
            const otherUrl = otherLinkEl ? otherLinkEl.getAttribute('href') : '';
            
            if (otherTitle && otherUrl) {
              allPoems.push({
                title: otherTitle,
                url: otherUrl,
                content: '' // Will be loaded on demand
              });
            }
          });
        }
        
        // Fetch poem content from URL
        if (poemUrl) {
          const currentPoem = {
            title: title,
            url: poemUrl,
            content: ''
          };
          fetchPoemContent(currentPoem, index, allPoems.length > 0 ? allPoems : null);
        }
      });
    });
  });
})();

