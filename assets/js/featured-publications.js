// Featured Publications Toggle Functionality
document.addEventListener('DOMContentLoaded', function() {
  const viewMoreButton = document.getElementById('view-more-featured');
  const hiddenItems = document.querySelectorAll('.featured-hidden');
  
  if (viewMoreButton && hiddenItems.length > 0) {
    let isExpanded = false;
    
    viewMoreButton.addEventListener('click', function() {
      if (isExpanded) {
        // Collapse - hide additional items
        hiddenItems.forEach(item => {
          item.style.display = 'none';
        });
        viewMoreButton.textContent = viewMoreButton.textContent.replace('Show less', 'View more featured items');
        isExpanded = false;
      } else {
        // Expand - show additional items
        hiddenItems.forEach(item => {
          item.style.display = 'block';
        });
        viewMoreButton.textContent = viewMoreButton.textContent.replace('View more featured items', 'Show less');
        isExpanded = true;
      }
    });
  }
});
