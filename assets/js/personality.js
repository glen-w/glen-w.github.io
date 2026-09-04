(function () {
  "use strict";

  if (document.documentElement.getAttribute("data-personality") === "off") {
    return;
  }

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var REVEAL_SELECTOR = [
    ".js-reveal",
    ".post > .post-header",
    ".post > article > p",
    ".post > article > h2",
    ".post .clearfix > p",
    ".post .header-bar",
    ".series-section",
    "#selectedPublicationsContainer",
    "#libraryApp > .library-search",
    "#libraryApp > .library-filters",
    ".projects > a",
  ].join(",");

  var SKIP_CLOSEST = "#libraryResults, .profile, .about-identity";

  function inFirstViewport(el) {
    var rect = el.getBoundingClientRect();
    return rect.top < window.innerHeight && rect.bottom > 0;
  }

  function initReveal() {
    if (reduceMotion || !("IntersectionObserver" in window)) {
      return;
    }

    var nodes = document.querySelectorAll(REVEAL_SELECTOR);
    if (!nodes.length) {
      return;
    }

    var io = new IntersectionObserver(
      function (entries) {
        for (var i = 0; i < entries.length; i++) {
          if (entries[i].isIntersecting) {
            entries[i].target.classList.add("is-in");
            io.unobserve(entries[i].target);
          }
        }
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
    );

    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      if (el.closest(SKIP_CLOSEST)) {
        continue;
      }
      if (inFirstViewport(el)) {
        continue;
      }
      el.classList.add("js-personality-reveal");
      io.observe(el);
    }
  }

  function start() {
    initReveal();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
