$(document).ready(function () {
  // add toggle functionality to abstract, award and bibtex buttons
  $("a.abstract").click(function () {
    // Close all other sections in this item
    $(this).parent().parent().find(".award.hidden.open, .bibtex.hidden.open, .quotes.hidden.open, .speakers.hidden.open, .video.hidden.open, .audio.hidden.open, .figures.hidden.open, .photos.hidden.open, .documents.hidden.open, .gallery.hidden.open").removeClass("open");
    // Toggle the abstract section
    $(this).parent().parent().find(".abstract.hidden").toggleClass("open");
  });
  $("a.award").click(function () {
    // Close all other sections in this item
    $(this).parent().parent().find(".abstract.hidden.open, .bibtex.hidden.open, .quotes.hidden.open, .speakers.hidden.open, .video.hidden.open, .audio.hidden.open, .figures.hidden.open, .photos.hidden.open, .documents.hidden.open, .gallery.hidden.open").removeClass("open");
    // Toggle the award section
    $(this).parent().parent().find(".award.hidden").toggleClass("open");
  });
  $("a.bibtex").click(function () {
    // Close all other sections in this item
    $(this).parent().parent().find(".abstract.hidden.open, .award.hidden.open, .quotes.hidden.open, .speakers.hidden.open, .video.hidden.open, .audio.hidden.open, .figures.hidden.open, .photos.hidden.open, .documents.hidden.open, .gallery.hidden.open").removeClass("open");
    // Toggle the bibtex section
    $(this).parent().parent().find(".bibtex.hidden").toggleClass("open");
  });
  $("a.quotes").click(function () {
    // Close all other sections in this item
    $(this).parent().parent().find(".abstract.hidden.open, .award.hidden.open, .bibtex.hidden.open, .speakers.hidden.open, .video.hidden.open, .audio.hidden.open, .figures.hidden.open, .photos.hidden.open, .documents.hidden.open, .gallery.hidden.open").removeClass("open");
    // Toggle the quotes section
    $(this).parent().parent().find(".quotes.hidden").toggleClass("open");
  });
  $("a.speakers").click(function () {
    // Close all other sections in this item
    $(this).parent().parent().find(".abstract.hidden.open, .award.hidden.open, .bibtex.hidden.open, .quotes.hidden.open, .video.hidden.open, .audio.hidden.open, .figures.hidden.open, .photos.hidden.open, .documents.hidden.open, .gallery.hidden.open").removeClass("open");
    // Toggle the speakers section
    $(this).parent().parent().find(".speakers.hidden").toggleClass("open");
  });
  $("a.video").click(function () {
    // Close all other sections in this item
    $(this).parent().parent().find(".abstract.hidden.open, .award.hidden.open, .bibtex.hidden.open, .quotes.hidden.open, .speakers.hidden.open, .audio.hidden.open, .figures.hidden.open, .photos.hidden.open, .documents.hidden.open, .gallery.hidden.open").removeClass("open");
    // Toggle the video section
    $(this).parent().parent().find(".video.hidden").toggleClass("open");
  });
  $("a.audio").click(function () {
    // Close all other sections in this item
    $(this).parent().parent().find(".abstract.hidden.open, .award.hidden.open, .bibtex.hidden.open, .quotes.hidden.open, .speakers.hidden.open, .video.hidden.open, .figures.hidden.open, .photos.hidden.open, .documents.hidden.open, .gallery.hidden.open").removeClass("open");
    // Toggle the audio section
    $(this).parent().parent().find(".audio.hidden").toggleClass("open");
  });
  $("a.figures").click(function () {
    // Close all other sections in this item
    $(this).parent().parent().find(".abstract.hidden.open, .award.hidden.open, .bibtex.hidden.open, .quotes.hidden.open, .speakers.hidden.open, .video.hidden.open, .audio.hidden.open, .photos.hidden.open, .documents.hidden.open, .gallery.hidden.open").removeClass("open");
    // Toggle the figures section
    $(this).parent().parent().find(".figures.hidden").toggleClass("open");
  });
  $("a.photos").click(function () {
    // Close all other sections in this item
    $(this).parent().parent().find(".abstract.hidden.open, .award.hidden.open, .bibtex.hidden.open, .quotes.hidden.open, .speakers.hidden.open, .video.hidden.open, .audio.hidden.open, .figures.hidden.open, .documents.hidden.open, .gallery.hidden.open").removeClass("open");
    // Toggle the photos section
    $(this).parent().parent().find(".photos.hidden").toggleClass("open");
  });
  $("a.documents").click(function () {
    // Close all other sections in this item
    $(this).parent().parent().find(".abstract.hidden.open, .award.hidden.open, .bibtex.hidden.open, .quotes.hidden.open, .speakers.hidden.open, .video.hidden.open, .audio.hidden.open, .figures.hidden.open, .photos.hidden.open, .gallery.hidden.open").removeClass("open");
    // Toggle the documents section
    $(this).parent().parent().find(".documents.hidden").toggleClass("open");
  });
  $("a.gallery").click(function () {
    // Close all other sections in this item
    $(this).parent().parent().find(".abstract.hidden.open, .award.hidden.open, .bibtex.hidden.open, .quotes.hidden.open, .speakers.hidden.open, .video.hidden.open, .audio.hidden.open, .figures.hidden.open, .photos.hidden.open, .documents.hidden.open").removeClass("open");
    // Toggle the gallery section
    $(this).parent().parent().find(".gallery.hidden").toggleClass("open");
  });
  $("a").removeClass("waves-effect waves-light");

  // bootstrap-toc
  if ($("#toc-sidebar").length) {
    // remove related publications years from the TOC
    $(".publications h2").each(function () {
      $(this).attr("data-toc-skip", "");
    });
    var navSelector = "#toc-sidebar";
    var $myNav = $(navSelector);
    Toc.init($myNav);
    $("body").scrollspy({
      target: navSelector,
    });
  }

  // add css to jupyter notebooks
  const cssLink = document.createElement("link");
  cssLink.href = "../css/jupyter.css";
  cssLink.rel = "stylesheet";
  cssLink.type = "text/css";

  let jupyterTheme = determineComputedTheme();

  $(".jupyter-notebook-iframe-container iframe").each(function () {
    $(this).contents().find("head").append(cssLink);

    if (jupyterTheme == "dark") {
      $(this).bind("load", function () {
        $(this).contents().find("body").attr({
          "data-jp-theme-light": "false",
          "data-jp-theme-name": "JupyterLab Dark",
        });
      });
    }
  });

  // trigger popovers
  $('[data-toggle="popover"]').popover({
    trigger: "hover",
  });
});

// Image modal functionality
function openImageModal(src, alt, galleryImages = null, currentIndex = 0) {
  // Create modal if it doesn't exist
  if (!document.getElementById('imageModal')) {
    const modal = document.createElement('div');
    modal.id = 'imageModal';
    modal.className = 'image-modal';
    modal.innerHTML = `
      <div class="image-modal-content">
        <span class="image-modal-close">&times;</span>
        <div class="image-modal-nav nav-arrow image-modal-prev" style="display: none;">
          <i class="fas fa-chevron-left"></i>
        </div>
        <div class="image-modal-nav nav-arrow image-modal-next" style="display: none;">
          <i class="fas fa-chevron-right"></i>
        </div>
        <img class="image-modal-img" src="" alt="">
        <div class="image-modal-caption"></div>
      </div>
    `;
    document.body.appendChild(modal);
    
    // Add event listeners
    modal.querySelector('.image-modal-close').onclick = closeImageModal;
    modal.querySelector('.image-modal-prev').onclick = function(e) {
      e.stopPropagation();
      navigateImage(-1);
    };
    modal.querySelector('.image-modal-next').onclick = function(e) {
      e.stopPropagation();
      navigateImage(1);
    };
    modal.onclick = function(event) {
      if (event.target === modal) {
        closeImageModal();
      }
    };
    
    // Add keyboard navigation
    document.addEventListener('keydown', handleImageModalKeydown);
  }
  
  // Store gallery context
  window.currentGallery = galleryImages;
  window.currentImageIndex = currentIndex;
  
  // Show modal
  const modal = document.getElementById('imageModal');
  const modalImg = modal.querySelector('.image-modal-img');
  const modalCaption = modal.querySelector('.image-modal-caption');
  const prevBtn = modal.querySelector('.image-modal-prev');
  const nextBtn = modal.querySelector('.image-modal-next');
  
  modalImg.src = src;
  modalCaption.textContent = '';
  
  // Show/hide navigation arrows based on gallery context
  if (galleryImages && galleryImages.length > 1) {
    prevBtn.style.display = 'block';
    nextBtn.style.display = 'block';
    updateNavigationButtons();
  } else {
    prevBtn.style.display = 'none';
    nextBtn.style.display = 'none';
  }
  
  modal.style.display = 'block';
}

// Navigation functions
function navigateImage(direction) {
  if (!window.currentGallery || window.currentGallery.length <= 1) return;
  
  window.currentImageIndex += direction;
  
  // Handle wrapping
  if (window.currentImageIndex < 0) {
    window.currentImageIndex = window.currentGallery.length - 1;
  } else if (window.currentImageIndex >= window.currentGallery.length) {
    window.currentImageIndex = 0;
  }
  
  // Update image and caption
  const modalImg = document.querySelector('.image-modal-img');
  const modalCaption = document.querySelector('.image-modal-caption');
  const currentImage = window.currentGallery[window.currentImageIndex];
  
  modalImg.src = currentImage.src;
  modalCaption.textContent = '';
  
  updateNavigationButtons();
}

function updateNavigationButtons() {
  if (!window.currentGallery || window.currentGallery.length <= 1) return;
  
  const prevBtn = document.querySelector('.image-modal-prev');
  const nextBtn = document.querySelector('.image-modal-next');
  
  // Enable/disable buttons based on current position
  prevBtn.style.opacity = window.currentImageIndex === 0 ? '0.5' : '1';
  nextBtn.style.opacity = window.currentImageIndex === window.currentGallery.length - 1 ? '0.5' : '1';
}

function handleImageModalKeydown(event) {
  const modal = document.getElementById('imageModal');
  if (!modal || modal.style.display === 'none') return;
  
  switch(event.key) {
    case 'ArrowLeft':
      event.preventDefault();
      navigateImage(-1);
      break;
    case 'ArrowRight':
      event.preventDefault();
      navigateImage(1);
      break;
    case 'Escape':
      event.preventDefault();
      closeImageModal();
      break;
  }
}

function closeImageModal() {
  const modal = document.getElementById('imageModal');
  if (modal) {
    modal.style.display = 'none';
  }
}

// Gallery modal function that collects gallery context
function openGalleryModal(clickedImage) {
  const galleryType = clickedImage.getAttribute('data-gallery-type');
  const currentIndex = parseInt(clickedImage.getAttribute('data-gallery-index'));
  
  // Find the parent gallery container
  const galleryContainer = clickedImage.closest('.gallery-grid');
  if (!galleryContainer) return;
  
  // Collect all images in this specific gallery
  const galleryImages = [];
  const allImages = galleryContainer.querySelectorAll('.gallery-image');
  
  allImages.forEach((img, index) => {
    galleryImages.push({
      src: img.src,
      alt: img.alt
    });
  });
  
  // Open modal with gallery context
  openImageModal(clickedImage.src, clickedImage.alt, galleryImages, currentIndex);
}
