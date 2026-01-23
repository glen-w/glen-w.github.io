/**
 * Carousel initialization and modal integration
 * Uses Swiper library for carousel functionality
 */

(function() {
  'use strict';

  // Wait for DOM and Swiper to be ready
  window.addEventListener('load', function() {
    // Check if Swiper is available
    if (typeof Swiper === 'undefined') {
      console.warn('Swiper not loaded. Carousel functionality disabled.');
      return;
    }

    // Initialize all carousels on the page
    const carouselContainers = document.querySelectorAll('.carousel-container');
    
    carouselContainers.forEach(function(container) {
      const carouselId = container.querySelector('.carousel-swiper').id;
      const seriesId = container.getAttribute('data-series-id');
      const seriesName = container.getAttribute('data-series-name');
      
      // Get all images in this series for modal gallery
      const allImages = [];
      const slides = container.querySelectorAll('.carousel-slide');
      slides.forEach(function(slide) {
        const img = slide.querySelector('img');
        if (img) {
          allImages.push({
            src: img.src,
            alt: img.alt || ''
          });
        }
      });

      // Initialize Swiper
      const swiper = new Swiper('#' + carouselId, {
        slidesPerView: 1,
        spaceBetween: 20,
        loop: false,
        navigation: {
          nextEl: container.querySelector('.carousel-button-next'),
          prevEl: container.querySelector('.carousel-button-prev'),
        },
        pagination: {
          el: container.querySelector('.carousel-pagination'),
          clickable: true,
          type: 'bullets',
        },
        keyboard: {
          enabled: true,
          onlyInViewport: true,
        },
        breakpoints: {
          640: {
            slidesPerView: 2,
            spaceBetween: 20,
          },
          768: {
            slidesPerView: 3,
            spaceBetween: 30,
          },
          1024: {
            slidesPerView: 4,
            spaceBetween: 40,
          },
        },
      });

      // Click handler for modal integration
      slides.forEach(function(slide, index) {
        const img = slide.querySelector('img');
        if (img) {
          img.style.cursor = 'pointer';
          img.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Get current slide index (accounting for Swiper's active index)
            const currentIndex = swiper.activeIndex;
            const realIndex = swiper.realIndex !== undefined ? swiper.realIndex : currentIndex;
            const clickedIndex = parseInt(slide.getAttribute('data-image-index')) || index;
            
            // Open modal with full series gallery
            if (typeof openImageModal === 'function') {
              openImageModal(img.src, img.alt || '', allImages, clickedIndex);
            } else {
              console.error('openImageModal function not found. Make sure common.js is loaded.');
            }
          });
        }
      });
    });
  });
})();

