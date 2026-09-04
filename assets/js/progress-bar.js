/*
 * This JavaScript code has been adapted from the article
 * https://css-tricks.com/reading-position-indicator/ authored by Pankaj Parashar,
 * published on the website https://css-tricks.com on the 7th of May, 2014.
 * Couple of changes were made to the original code to make it compatible
 * with the `al-folio` theme.
 *
 * Dynamic pages (e.g. /library/) grow after initial paint. Expose
 * refreshProgressBar() and observe size changes so max is recomputed
 * when document height changes — otherwise a short shell makes max≈0
 * and the bar jumps to full.
 */
(function () {
  const progressBar = $("#progress");
  if (!progressBar.length) return;

  let setupDone = false;
  let refreshTimer = null;
  const supportsProgress = "max" in document.createElement("progress");

  /*
   * We set up the bar after all elements are done loading.
   * In some cases, if the images in the page are larger than the intended
   * size they'll have on the page, they'll be resized via CSS to accomodate
   * the desired size. This mistake, however, breaks the computations as the
   * scroll size is computed as soon as the elements finish loading.
   * To account for this, a minimal delay was introduced before computing the
   * values.
   */
  window.onload = function () {
    setTimeout(progressBarSetup, 50);
  };

  function progressBarSetup() {
    if (!setupDone) {
      setupDone = true;
      if (supportsProgress) {
        initializeProgressElement();
        $(document).on("scroll", function () {
          progressBar.attr({ value: getCurrentScrollPosition() });
        });
        $(window).on("resize", scheduleRefresh);
      } else {
        resizeProgressBar();
        $(document).on("scroll", resizeProgressBar);
        $(window).on("resize", scheduleRefresh);
      }
      observeDynamicHeight();
    } else {
      refreshProgressBar();
    }
  }

  /*
   * The vertical scroll position is the same as the number of pixels that
   * are hidden from view above the scrollable area. Thus, a value > 0 is
   * how much the user has scrolled from the top
   */
  function getCurrentScrollPosition() {
    return $(window).scrollTop();
  }

  function initializeProgressElement() {
    let navbarHeight = $("#navbar").outerHeight(true);
    $("body").css({ "padding-top": navbarHeight });
    $("progress-container").css({ "padding-top": navbarHeight });
    progressBar.css({ top: navbarHeight });
    applyProgressMetrics();
  }

  /*
   * The offset between the html document height and the browser viewport
   * height will be greater than zero if vertical scroll is possible.
   * This is the distance the user can scroll
   */
  function getDistanceToScroll() {
    return Math.max(0, $(document).height() - $(window).height());
  }

  function applyProgressMetrics() {
    const distance = getDistanceToScroll();
    // max=0 makes <progress> appear complete in some browsers; keep empty at top.
    progressBar.attr({
      max: distance > 0 ? distance : 1,
      value: distance > 0 ? getCurrentScrollPosition() : 0,
    });
  }

  function resizeProgressBar() {
    progressBar.css({ width: getWidthPercentage() + "%" });
  }

  // The scroll ratio equals the percentage to resize the bar
  function getWidthPercentage() {
    const distance = getDistanceToScroll();
    if (distance <= 0) return 0;
    return (getCurrentScrollPosition() / distance) * 100;
  }

  function refreshProgressBar() {
    if (!setupDone) return;
    if (supportsProgress) {
      applyProgressMetrics();
    } else {
      resizeProgressBar();
    }
  }

  function scheduleRefresh() {
    clearTimeout(refreshTimer);
    refreshTimer = setTimeout(refreshProgressBar, 50);
  }

  function observeDynamicHeight() {
    if (typeof ResizeObserver === "undefined") return;

    const observer = new ResizeObserver(scheduleRefresh);
    if (document.body) observer.observe(document.body);
    if (document.documentElement) observer.observe(document.documentElement);

    const libraryResults = document.getElementById("libraryResults");
    if (libraryResults) observer.observe(libraryResults);
  }

  // Hook for dynamic pages (library catalog render/filter) and tests.
  window.refreshProgressBar = scheduleRefresh;
})();
