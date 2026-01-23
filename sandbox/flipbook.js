/**
 * Flipbook initialization and modal integration
 * Uses Turn.js library for page flip animations
 */

(function() {
  'use strict';

  // Fallback navigation function when Turn.js is not available
  // Defined early so it's available for immediate fallback
  function setupFallbackNavigation(container, pages) {
    console.log('[FLIPBOOK DEBUG] setupFallbackNavigation called with', pages.length, 'pages');
    let currentPageIndex = 0;
    const totalPages = pages.length;
    const flipbook = container.querySelector('.flipbook');
    
    // Ensure flipbook has the initialized class so CSS shows pages
    if (flipbook) {
      flipbook.classList.add('turnjs-initialized');
      console.log('[FLIPBOOK DEBUG] Added turnjs-initialized class to flipbook');
    } else {
      console.error('[FLIPBOOK DEBUG] Flipbook element not found in container!');
      return;
    }
    
    function showPage(index) {
      console.log('[FLIPBOOK DEBUG] showPage called with index', index);
      pages.forEach(function(page, i) {
        if (i === index) {
          // Force visibility with inline styles that override CSS
          page.style.setProperty('display', 'block', 'important');
          page.style.setProperty('visibility', 'visible', 'important');
          page.style.setProperty('opacity', '1', 'important');
          page.style.setProperty('position', 'relative', 'important');
          console.log('[FLIPBOOK DEBUG] Showing page', i, 'computed display:', window.getComputedStyle(page).display);
        } else {
          page.style.setProperty('display', 'none', 'important');
        }
      });
      
      const indicator = container.querySelector('.flipbook-current-page');
      if (indicator) {
        indicator.textContent = index + 1;
      }
      
      const totalPagesEl = container.querySelector('.flipbook-total-pages');
      if (totalPagesEl) {
        totalPagesEl.textContent = totalPages;
      }
    }
    
    const prevBtn = container.querySelector('.flipbook-prev');
    const nextBtn = container.querySelector('.flipbook-next');
    
    // Remove existing listeners by cloning buttons
    if (prevBtn) {
      const newPrevBtn = prevBtn.cloneNode(true);
      prevBtn.parentNode.replaceChild(newPrevBtn, prevBtn);
      newPrevBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        if (currentPageIndex > 0) {
          currentPageIndex--;
          showPage(currentPageIndex);
        }
      });
    }
    
    if (nextBtn) {
      const newNextBtn = nextBtn.cloneNode(true);
      nextBtn.parentNode.replaceChild(newNextBtn, nextBtn);
      newNextBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        if (currentPageIndex < totalPages - 1) {
          currentPageIndex++;
          showPage(currentPageIndex);
        }
      });
    }
    
    // Show first page immediately
    console.log('[FLIPBOOK DEBUG] About to show first page');
    showPage(0);
    console.log('[FLIPBOOK DEBUG] Fallback navigation set up for', totalPages, 'pages');
    
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/0dedbb0d-968d-4d41-95ef-f9c65a7029fa', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        location: 'flipbook.js:setupFallbackNavigation',
        message: 'Fallback navigation completed',
        data: {
          totalPages: totalPages,
          flipbookHasClass: flipbook.classList.contains('turnjs-initialized'),
          firstPageVisible: pages[0] ? window.getComputedStyle(pages[0]).display !== 'none' : false
        },
        timestamp: Date.now(),
        sessionId: 'debug-session',
        runId: 'run1',
        hypothesisId: 'E'
      })
    }).catch(() => {});
    // #endregion
  }

  // Function to measure all images and calculate optimal viewport size
  // This ensures all images (including larger covers) fit without cropping
  function calculateOptimalViewportSize(pages, containerWidth, containerHeight) {
    return new Promise(function(resolve) {
      const images = [];
      let loadedCount = 0;
      const totalImages = pages.length;
      
      // If no images, use default dimensions
      if (totalImages === 0) {
        resolve({
          width: containerWidth || 1000,
          height: containerHeight || 800
        });
        return;
      }
      
      // Collect all images and wait for them to load
      pages.forEach(function(page) {
        const img = page.querySelector('img');
        if (img) {
          // If image is already loaded, use its dimensions immediately
          if (img.complete && img.naturalWidth > 0) {
            images.push({
              width: img.naturalWidth,
              height: img.naturalHeight
            });
            loadedCount++;
            checkComplete();
          } else {
            // Wait for image to load
            const onLoad = function() {
              images.push({
                width: img.naturalWidth,
                height: img.naturalHeight
              });
              loadedCount++;
              img.removeEventListener('load', onLoad);
              img.removeEventListener('error', onError);
              checkComplete();
            };
            const onError = function() {
              // If image fails to load, use a default size
              images.push({
                width: 800,
                height: 600
              });
              loadedCount++;
              img.removeEventListener('load', onLoad);
              img.removeEventListener('error', onError);
              checkComplete();
            };
            img.addEventListener('load', onLoad);
            img.addEventListener('error', onError);
          }
        } else {
          // No image in this page, count it as loaded
          loadedCount++;
          checkComplete();
        }
      });
      
      function checkComplete() {
        if (loadedCount >= totalImages) {
          // Calculate maximum dimensions needed
          // Account for padding: page content has 1rem (~16px) padding on each side = 32px total
          // Cover pages have 2rem (~32px) padding on each side = 64px total
          // Use the larger padding to ensure cover images fit
          const padding = 64;
          const maxWidth = Math.max.apply(null, images.map(function(img) { return img.width; }).concat([800]));
          const maxHeight = Math.max.apply(null, images.map(function(img) { return img.height; }).concat([600]));
          
          // Use container dimensions as base, but ensure we can fit the largest image
          // Account for container padding (1rem 4rem = ~64px horizontal padding)
          const containerPadding = 128; // 4rem on each side
          const baseWidth = Math.min((containerWidth || 1000) - containerPadding, window.innerWidth * 0.95);
          // Use viewport height as a better base for portrait images (80vh)
          const viewportHeight = window.innerHeight * 0.8; // 80vh
          const baseHeight = Math.max(containerHeight || viewportHeight, viewportHeight);
          
          // Calculate the dimensions needed to fit the largest image with padding
          const requiredWidth = maxWidth + padding;
          const requiredHeight = maxHeight + padding;
          
          // For portrait images, prioritize fitting the full height
          // Calculate ratios to see which dimension needs more space
          const widthRatio = requiredWidth / baseWidth;
          const heightRatio = requiredHeight / baseHeight;
          
          // Use the larger ratio to ensure both dimensions fit
          // This is especially important for portrait images
          const maxRatio = Math.max(1, widthRatio, heightRatio);
          
          // Calculate optimal dimensions, ensuring aspect ratio is maintained
          let optimalWidth = Math.ceil(baseWidth * maxRatio);
          let optimalHeight = Math.ceil(baseHeight * maxRatio);
          
          // Cap dimensions to viewport limits (80vh max height, 95% width accounting for padding)
          const maxViewportHeight = window.innerHeight * 0.8; // 80vh
          const maxViewportWidth = window.innerWidth * 0.95; // Account for container padding
          const maxWidthLimit = Math.min(2000, maxViewportWidth);
          const maxHeightLimit = Math.max(1600, maxViewportHeight);
          
          let finalWidth = optimalWidth;
          let finalHeight = optimalHeight;
          
          // Scale down if width exceeds limit
          if (finalWidth > maxWidthLimit) {
            const scale = maxWidthLimit / finalWidth;
            finalWidth = maxWidthLimit;
            finalHeight = Math.ceil(finalHeight * scale);
          }
          
          // Scale down if height exceeds limit (capped at 80vh)
          if (finalHeight > maxHeightLimit) {
            const scale = maxHeightLimit / finalHeight;
            finalHeight = maxHeightLimit;
            finalWidth = Math.ceil(finalWidth * scale);
          }
          
          // Final check: ensure height never exceeds 80vh
          if (finalHeight > maxViewportHeight) {
            const scale = maxViewportHeight / finalHeight;
            finalHeight = maxViewportHeight;
            finalWidth = Math.ceil(finalWidth * scale);
          }
          
          resolve({
            width: finalWidth,
            height: finalHeight
          });
        }
      }
      
      // Timeout fallback: if images don't load within 3 seconds, use defaults
      setTimeout(function() {
        if (loadedCount < totalImages) {
          console.warn('[FLIPBOOK] Some images did not load in time, using calculated dimensions');
          checkComplete();
        }
      }, 3000);
    });
  }

  // Immediate fallback: Check if Turn.js script failed to load
  // This runs immediately, not waiting for load event
  function checkAndSetupFallback() {
    const containers = document.querySelectorAll('.flipbook-container');
    if (containers.length === 0) return;
    
    // If Turn.js isn't available after a short delay, use fallback
    setTimeout(function() {
      if (typeof jQuery === 'undefined' || typeof jQuery.fn.turn === 'undefined') {
        console.log('[FLIPBOOK DEBUG] Turn.js not available, setting up immediate fallback');
        containers.forEach(function(container) {
          const flipbook = container.querySelector('.flipbook');
          if (flipbook && !flipbook.classList.contains('turnjs-initialized')) {
            const pages = container.querySelectorAll('.flipbook-page');
            if (pages.length > 0) {
              flipbook.classList.add('turnjs-initialized');
              setupFallbackNavigation(container, pages);
            }
          }
        });
      }
    }, 1000); // Check after 1 second
  }
  
  // Run check immediately if DOM is ready, otherwise wait
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', checkAndSetupFallback);
  } else {
    checkAndSetupFallback();
  }

  // Wait for DOM and Turn.js to be ready
  window.addEventListener('load', function() {
    console.log('[FLIPBOOK DEBUG] Window load event fired');
    // Wait a bit for jQuery and Turn.js to load
    setTimeout(function() {
      console.log('[FLIPBOOK DEBUG] Timeout fired, checking libraries');
      // Check if Turn.js is available
      if (typeof jQuery === 'undefined' || typeof jQuery.fn.turn === 'undefined') {
        console.warn('[FLIPBOOK DEBUG] Turn.js not loaded. Using fallback navigation.');
        console.warn('jQuery available:', typeof jQuery !== 'undefined');
        console.warn('Turn.js available:', typeof jQuery !== 'undefined' && typeof jQuery.fn.turn !== 'undefined');
        
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/0dedbb0d-968d-4d41-95ef-f9c65a7029fa', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            location: 'flipbook.js:14',
            message: 'Turn.js not available - using fallback',
            data: {
              jqueryAvailable: typeof jQuery !== 'undefined',
              turnAvailable: typeof jQuery !== 'undefined' && typeof jQuery.fn.turn !== 'undefined'
            },
            timestamp: Date.now(),
            sessionId: 'debug-session',
            runId: 'run1',
            hypothesisId: 'E'
          })
        }).catch(() => {});
        // #endregion
        
        // FALLBACK: Show pages even without Turn.js
        const flipbookContainers = document.querySelectorAll('.flipbook-container');
        console.log('[FLIPBOOK DEBUG] Found', flipbookContainers.length, 'containers for fallback');
        flipbookContainers.forEach(function(container, idx) {
          const flipbook = container.querySelector('.flipbook');
          if (flipbook) {
            console.log('[FLIPBOOK DEBUG] Setting up fallback for container', idx);
            flipbook.classList.add('turnjs-initialized');
            const pages = container.querySelectorAll('.flipbook-page');
            console.log('[FLIPBOOK DEBUG] Found', pages.length, 'pages in container', idx);
            setupFallbackNavigation(container, pages);
          } else {
            console.error('[FLIPBOOK DEBUG] No flipbook element found in container', idx);
          }
        });
        return;
      }
      
      console.log('[FLIPBOOK DEBUG] Libraries available, proceeding');

      // Initialize all flipbooks on the page
      const flipbookContainers = document.querySelectorAll('.flipbook-container');
      console.log('[FLIPBOOK DEBUG] Found', flipbookContainers.length, 'flipbook containers');
      
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/0dedbb0d-968d-4d41-95ef-f9c65a7029fa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          location: 'flipbook.js:22',
          message: 'Flipbook initialization start',
          data: { containersFound: flipbookContainers.length },
          timestamp: Date.now(),
          sessionId: 'debug-session',
          runId: 'run1',
          hypothesisId: 'D'
        })
      }).catch(() => {});
      // #endregion
      
      flipbookContainers.forEach(function(container) {
        const flipbookId = container.querySelector('.flipbook').id;
        const seriesId = container.getAttribute('data-series-id');
        const seriesName = container.getAttribute('data-series-name');
        
        // Get all images in this series for modal gallery
        const allImages = [];
        const pages = container.querySelectorAll('.flipbook-page');
        
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/0dedbb0d-968d-4d41-95ef-f9c65a7029fa', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            location: 'flipbook.js:32',
            message: 'Pages found in container',
            data: {
              flipbookId: flipbookId,
              seriesId: seriesId,
              pagesCount: pages.length,
              pagesWithImages: Array.from(pages).filter(p => p.querySelector('img')).length
            },
            timestamp: Date.now(),
            sessionId: 'debug-session',
            runId: 'run1',
            hypothesisId: 'C'
          })
        }).catch(() => {});
        // #endregion
        
        pages.forEach(function(page) {
          const img = page.querySelector('img');
          if (img) {
            allImages.push({
              src: img.src,
              alt: img.alt || ''
            });
          }
        });

        // Initialize Turn.js
        const $flipbook = jQuery('#' + flipbookId);
        
        // Verify flipbook element exists
        if ($flipbook.length === 0) {
          // #region agent log
          fetch('http://127.0.0.1:7242/ingest/0dedbb0d-968d-4d41-95ef-f9c65a7029fa', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              location: 'flipbook.js:46',
              message: 'Flipbook element not found',
              data: { flipbookId: flipbookId },
              timestamp: Date.now(),
              sessionId: 'debug-session',
              runId: 'run1',
              hypothesisId: 'E'
            })
          }).catch(() => {});
          // #endregion
          console.warn('Flipbook element not found:', flipbookId);
          return;
        }
        
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/0dedbb0d-968d-4d41-95ef-f9c65a7029fa', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            location: 'flipbook.js:51',
            message: 'Before Turn.js initialization',
            data: {
              flipbookId: flipbookId,
              pagesCount: pages.length,
              hasImages: allImages.length > 0,
              jqueryAvailable: typeof jQuery !== 'undefined',
              turnAvailable: typeof jQuery !== 'undefined' && typeof jQuery.fn.turn !== 'undefined'
            },
            timestamp: Date.now(),
            sessionId: 'debug-session',
            runId: 'run1',
            hypothesisId: 'E'
          })
        }).catch(() => {});
        // #endregion
        
        try {
          // Mark as initializing to prevent flash of unstyled content
          $flipbook.addClass('turnjs-initializing');
          
          // Get base dimensions from the element (now using viewport height from CSS)
          const baseWidth = $flipbook.width() || 1000;
          // Use viewport height as base (80vh)
          const viewportHeight = window.innerHeight * 0.8; // 80vh
          const baseHeight = Math.max($flipbook.height() || viewportHeight, viewportHeight);
          
          // Calculate optimal viewport size based on actual image dimensions
          // This ensures larger cover images and portrait images don't get cropped
          calculateOptimalViewportSize(pages, baseWidth, baseHeight).then(function(dimensions) {
            let flipbookWidth = dimensions.width;
            let flipbookHeight = dimensions.height;
            
            // Cap dimensions to viewport limits before applying
            const maxViewportHeight = window.innerHeight * 0.8; // 80vh
            const maxViewportWidth = window.innerWidth * 0.95; // Account for container padding
            
            // Ensure height never exceeds 80vh
            if (flipbookHeight > maxViewportHeight) {
              const scale = maxViewportHeight / flipbookHeight;
              flipbookHeight = maxViewportHeight;
              flipbookWidth = Math.ceil(flipbookWidth * scale);
            }
            
            // Ensure width doesn't exceed viewport (accounting for container padding)
            if (flipbookWidth > maxViewportWidth) {
              const scale = maxViewportWidth / flipbookWidth;
              flipbookWidth = maxViewportWidth;
              flipbookHeight = Math.ceil(flipbookHeight * scale);
            }
            
            // Always update flipbook size to ensure images fit properly
            // This is especially important for portrait images
            $flipbook.css({
              width: flipbookWidth + 'px',
              height: flipbookHeight + 'px'
            });
            
            $flipbook.turn({
              width: flipbookWidth,
              height: flipbookHeight,
              autoCenter: true,
              pages: pages.length,
              gradients: true,
              elevation: 50,
              when: {
                turning: function(event, page, view) {
                  // Update page indicator
                  const indicator = container.querySelector('.flipbook-current-page');
                  if (indicator) {
                    indicator.textContent = page;
                  }
                },
                end: function(event, pageObject, corner) {
                  // Mark as initialized after first render
                  $flipbook.addClass('turnjs-initialized').removeClass('turnjs-initializing');
                  
                  // #region agent log
                  fetch('http://127.0.0.1:7242/ingest/0dedbb0d-968d-4d41-95ef-f9c65a7029fa', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                      location: 'flipbook.js:73',
                      message: 'Turn.js initialization complete',
                      data: { 
                        flipbookId: flipbookId, 
                        page: pageObject,
                        viewportWidth: flipbookWidth,
                        viewportHeight: flipbookHeight
                      },
                      timestamp: Date.now(),
                      sessionId: 'debug-session',
                      runId: 'run1',
                      hypothesisId: 'E'
                    })
                  }).catch(() => {});
                  // #endregion
                }
              }
            });
            
            // Fallback: mark as initialized after a short delay
            setTimeout(function() {
              $flipbook.addClass('turnjs-initialized').removeClass('turnjs-initializing');
            }, 100);
          }).catch(function(error) {
            console.error('[FLIPBOOK] Error calculating viewport size:', error);
            // Fallback to base dimensions
            $flipbook.turn({
              width: baseWidth,
              height: baseHeight,
              autoCenter: true,
              pages: pages.length,
              gradients: true,
              elevation: 50,
              when: {
                turning: function(event, page, view) {
                  const indicator = container.querySelector('.flipbook-current-page');
                  if (indicator) {
                    indicator.textContent = page;
                  }
                },
                end: function(event, pageObject, corner) {
                  $flipbook.addClass('turnjs-initialized').removeClass('turnjs-initializing');
                }
              }
            });
          });
        } catch (error) {
          // #region agent log
          fetch('http://127.0.0.1:7242/ingest/0dedbb0d-968d-4d41-95ef-f9c65a7029fa', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              location: 'flipbook.js:95',
              message: 'Turn.js initialization error',
              data: {
                flipbookId: flipbookId,
                error: error.message,
                stack: error.stack
              },
              timestamp: Date.now(),
              sessionId: 'debug-session',
              runId: 'run1',
              hypothesisId: 'E'
            })
          }).catch(() => {});
          // #endregion
          console.error('[FLIPBOOK DEBUG] Error initializing Turn.js for flipbook:', flipbookId, error);
          // Show pages even if Turn.js fails - CRITICAL FALLBACK
          $flipbook.addClass('turnjs-initialized').removeClass('turnjs-initializing');
          console.log('[FLIPBOOK DEBUG] Applied fallback: showing pages without Turn.js');
          // Still set up basic navigation without Turn.js
          setupFallbackNavigation(container, pages);
          return;
        }
        
        // Fallback: If Turn.js doesn't initialize within 2 seconds, show pages anyway
        setTimeout(function() {
          if (!$flipbook.hasClass('turnjs-initialized') && !$flipbook.hasClass('turnjs-initializing')) {
            console.warn('[FLIPBOOK DEBUG] Turn.js initialization timeout - showing pages as fallback');
            $flipbook.addClass('turnjs-initialized');
            setupFallbackNavigation(container, pages);
          }
        }, 2000);

        // Verify Turn.js is initialized before attaching navigation
        if (!$flipbook.data('turn')) {
          // #region agent log
          fetch('http://127.0.0.1:7242/ingest/0dedbb0d-968d-4d41-95ef-f9c65a7029fa', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              location: 'flipbook.js:108',
              message: 'Turn.js data check failed',
              data: { flipbookId: flipbookId, hasTurnData: !!$flipbook.data('turn') },
              timestamp: Date.now(),
              sessionId: 'debug-session',
              runId: 'run1',
              hypothesisId: 'E'
            })
          }).catch(() => {});
          // #endregion
          console.warn('Turn.js not initialized for flipbook:', flipbookId);
          return;
        }
        
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/0dedbb0d-968d-4d41-95ef-f9c65a7029fa', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            location: 'flipbook.js:120',
            message: 'Turn.js successfully initialized',
            data: {
              flipbookId: flipbookId,
              pagesCount: pages.length,
              visiblePages: container.querySelectorAll('.flipbook-page:not([style*="display: none"])').length
            },
            timestamp: Date.now(),
            sessionId: 'debug-session',
            runId: 'run1',
            hypothesisId: 'D'
          })
        }).catch(() => {});
        // #endregion

        // Navigation buttons - use closure to ensure correct flipbook instance
        const prevBtn = container.querySelector('.flipbook-prev');
        const nextBtn = container.querySelector('.flipbook-next');
        
        if (prevBtn) {
          prevBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            if ($flipbook.data('turn')) {
              $flipbook.turn('previous');
            } else {
              console.warn('Turn.js not initialized, cannot navigate');
            }
          });
        } else {
          console.warn('Previous button not found for flipbook:', flipbookId);
        }
        
        if (nextBtn) {
          nextBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            if ($flipbook.data('turn')) {
              $flipbook.turn('next');
            } else {
              console.warn('Turn.js not initialized, cannot navigate');
            }
          });
        } else {
          console.warn('Next button not found for flipbook:', flipbookId);
        }

        // Keyboard navigation - use closure to ensure correct flipbook instance
        const keyboardHandler = function(e) {
          // Only handle if flipbook is in view
          const rect = container.getBoundingClientRect();
          const inView = rect.top < window.innerHeight && rect.bottom > 0;
          
          if (inView && (e.key === 'ArrowLeft' || e.key === 'ArrowRight')) {
            if (!$flipbook.data('turn')) {
              return; // Don't prevent default if Turn.js not ready
            }
            e.preventDefault();
            if (e.key === 'ArrowLeft') {
              $flipbook.turn('previous');
            } else {
              $flipbook.turn('next');
            }
          }
        };
        document.addEventListener('keydown', keyboardHandler);

        // Click handler for modal integration
        pages.forEach(function(page, index) {
          const img = page.querySelector('img');
          if (img) {
            img.style.cursor = 'pointer';
            img.addEventListener('click', function(e) {
              e.preventDefault();
              e.stopPropagation();
              
              // Open modal with full series gallery
              if (typeof openImageModal === 'function') {
                openImageModal(img.src, img.alt || '', allImages, index);
              } else {
                console.error('openImageModal function not found. Make sure common.js is loaded.');
              }
            });
          }
        });

        // Update total pages indicator
        const totalPagesEl = container.querySelector('.flipbook-total-pages');
        if (totalPagesEl) {
          totalPagesEl.textContent = pages.length;
        }
      });

      // Handle responsive resizing
      let resizeTimer;
      window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
          flipbookContainers.forEach(function(container) {
            const flipbookId = container.querySelector('.flipbook').id;
            const $flipbook = jQuery('#' + flipbookId);
            if ($flipbook.data('turn')) {
              $flipbook.turn('size', $flipbook.width(), $flipbook.height());
            }
          });
        }, 250);
      });
    }, 500); // Wait 500ms for libraries to load
  });
})();

