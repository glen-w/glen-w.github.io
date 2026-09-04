module.exports = {
  content: ["_site/**/*.html", "_site/**/*.js"],
  css: ["_site/assets/css/*.css"],
  output: "_site/assets/css/",
  skippedContentGlobs: ["_site/assets/**/*.html"],
  // Contribution levels are applied via JS (`day-${level}`), so PurgeCSS
  // never sees the full class names in content and would strip the swatches.
  safelist: [
    "github-contributions-day-0",
    "github-contributions-day-1",
    "github-contributions-day-2",
    "github-contributions-day-3",
    "github-contributions-day-4",
  ],
};
