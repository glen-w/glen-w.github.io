/**
 * Masonry layout initialization and modal integration
 * Uses Masonry.js library for Pinterest-style staggered grid
 */

(function() {
  'use strict';

  // Wait for DOM and libraries to be ready
  window.addEventListener('load', function() {
    // Check if Masonry and imagesLoaded are available
    if (typeof Masonry === 'undefined') {
      console.warn('Masonry.js not loaded. Masonry layout functionality disabled.');
      return;
    }
    
    if (typeof imagesLoaded === 'undefined') {
      console.warn('imagesLoaded not available. Masonry may not work correctly.');
    }

    // Initialize all masonry grids on the page
    const masonryContainers = document.querySelectorAll('.masonry-container');
    
    masonryContainers.forEach(function(container) {
      const gridId = container.querySelector('.masonry-grid').id;
      const seriesId = container.getAttribute('data-series-id');
      const seriesName = container.getAttribute('data-series-name');
      
      // Get all images in this series for modal gallery
      const allImages = [];
      const items = container.querySelectorAll('.masonry-item');
      items.forEach(function(item) {
        const img = item.querySelector('img');
        if (img) {
          allImages.push({
            src: img.src,
            alt: img.alt || ''
          });
        }
      });

      const grid = document.getElementById(gridId);
      
      // Initialize Masonry with imagesLoaded
      if (typeof imagesLoaded !== 'undefined') {
        imagesLoaded(grid, function() {
          // Calculate column width based on container and responsive breakpoints
          // Account for container padding (1rem = ~16px on each side = 32px total)
          const containerWidth = grid.offsetWidth;
          const gutter = 20;
          let columnWidth;
          
          if (containerWidth < 480) {
            // 1 column on mobile
            columnWidth = containerWidth;
          } else if (containerWidth < 768) {
            // 2 columns on tablet: (width - 1 gutter) / 2
            columnWidth = (containerWidth - gutter) / 2;
          } else if (containerWidth < 1024) {
            // 3 columns on desktop: (width - 2 gutters) / 3
            columnWidth = (containerWidth - (gutter * 2)) / 3;
          } else {
            // 4 columns on large screens: (width - 3 gutters) / 4
            columnWidth = (containerWidth - (gutter * 3)) / 4;
          }
          
          // Set explicit width on all items before initializing Masonry
          const items = grid.querySelectorAll('.masonry-item');
          items.forEach(function(item) {
            item.style.width = columnWidth + 'px';
          });
          
          const msnry = new Masonry(grid, {
            itemSelector: '.masonry-item',
            columnWidth: columnWidth,
            percentPosition: false,
            gutter: 20,
            fitWidth: false,
            transitionDuration: '0.2s'
          });
          
          // Store Masonry instance for later use
          grid.masonryInstance = msnry;
          
          // Force layout recalculation
          msnry.layout();
          
          // Recalculate layout on window resize
          let resizeTimer;
          const resizeHandler = function() {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(function() {
              if (msnry) {
                // Recalculate column width on resize
                const containerWidth = grid.offsetWidth;
                const gutter = 20;
                let newColumnWidth;
                
                if (containerWidth < 480) {
                  newColumnWidth = containerWidth;
                } else if (containerWidth < 768) {
                  newColumnWidth = (containerWidth - gutter) / 2;
                } else if (containerWidth < 1024) {
                  newColumnWidth = (containerWidth - (gutter * 2)) / 3;
                } else {
                  newColumnWidth = (containerWidth - (gutter * 3)) / 4;
                }
                
                msnry.columnWidth = newColumnWidth;
                
                // Update all item widths to match new column width
                const items = grid.querySelectorAll('.masonry-item');
                items.forEach(function(item) {
                  item.style.width = newColumnWidth + 'px';
                });
                
                msnry.layout();
              }
            }, 250);
          };
          window.addEventListener('resize', resizeHandler);
        });
      } else {
        // Fallback if imagesLoaded not available
        const containerWidth = grid.offsetWidth;
        const gutter = 20;
        let columnWidth;
        
        if (containerWidth < 480) {
          columnWidth = containerWidth;
        } else if (containerWidth < 768) {
          columnWidth = (containerWidth - gutter) / 2;
        } else if (containerWidth < 1024) {
          columnWidth = (containerWidth - (gutter * 2)) / 3;
        } else {
          columnWidth = (containerWidth - (gutter * 3)) / 4;
        }
        
        // Set explicit width on all items before initializing Masonry
        const items = grid.querySelectorAll('.masonry-item');
        items.forEach(function(item) {
          item.style.width = columnWidth + 'px';
        });
        
        const msnry = new Masonry(grid, {
          itemSelector: '.masonry-item',
          columnWidth: columnWidth,
          percentPosition: false,
          gutter: 20,
          fitWidth: false,
          transitionDuration: '0.2s'
        });
        
        grid.masonryInstance = msnry;
        
        // Force layout recalculation
        msnry.layout();
      }

      // Click handler for modal integration
      items.forEach(function(item, index) {
        const img = item.querySelector('img');
        if (img) {
          img.style.cursor = 'pointer';
          item.style.cursor = 'pointer';
          
          item.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Get image index
            const imageIndex = parseInt(item.getAttribute('data-image-index')) || index;
            
            // Open modal with full series gallery
            if (typeof openImageModal === 'function') {
              openImageModal(img.src, img.alt || '', allImages, imageIndex);
            } else {
              console.error('openImageModal function not found. Make sure common.js is loaded.');
            }
          });
        }
      });
    });
  });
})();

