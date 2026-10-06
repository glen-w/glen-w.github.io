/**
 * Homepage role line: type / delete cycle (poetry-typewriter style).
 */
(function () {
  "use strict";

  const root = document.querySelector(".role-typewriter");
  if (!root) {
    return;
  }

  const staticEl = document.querySelector(".role-typewriter-static");
  const articleEl = document.querySelector(".role-typewriter-article");
  const wordEl = root.querySelector(".role-typewriter__word");
  if (!wordEl) {
    return;
  }

  const roles = (root.getAttribute("data-roles") || "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);

  if (roles.length === 0) {
    return;
  }

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reducedMotion) {
    return;
  }

  if (staticEl) {
    staticEl.hidden = true;
  }
  if (articleEl) {
    articleEl.hidden = false;
  }
  root.hidden = false;

  function indefiniteArticle(word) {
    if (!word) {
      return "a";
    }
    const first = word.trim().charAt(0).toLowerCase();
    if (first === "a" || first === "e" || first === "i" || first === "o") {
      return "an";
    }
    return "a";
  }

  function syncArticle() {
    if (!articleEl) {
      return;
    }
    articleEl.textContent = indefiniteArticle(currentWord());
  }

  function shuffleInPlace(list) {
    for (let i = list.length - 1; i > 0; i -= 1) {
      const j = Math.floor(Math.random() * (i + 1));
      const tmp = list[i];
      list[i] = list[j];
      list[j] = tmp;
    }
    return list;
  }

  shuffleInPlace(roles);

  const TYPE_MS = 42;
  const DELETE_MS = 26;
  const HOLD_MS = 2400;

  let roleIndex = 0;
  let charIndex = 0;
  let deleting = false;
  let timerId = null;

  wordEl.textContent = "";
  wordEl.classList.add("is-active");

  function currentWord() {
    return roles[roleIndex];
  }

  function setWordSlice(length) {
    wordEl.textContent = currentWord().slice(0, length);
    if (length > 0) {
      syncArticle();
    }
  }

  function schedule(delay, fn) {
    if (timerId !== null) {
      clearTimeout(timerId);
    }
    timerId = window.setTimeout(fn, delay);
  }

  function tick() {
    const word = currentWord();

    if (!deleting) {
      if (charIndex < word.length) {
        charIndex += 1;
        setWordSlice(charIndex);
        wordEl.classList.remove("is-paused");
        schedule(TYPE_MS, tick);
        return;
      }

      deleting = true;
      wordEl.classList.add("is-paused");
      schedule(HOLD_MS, tick);
      return;
    }

    if (charIndex > 0) {
      charIndex -= 1;
      setWordSlice(charIndex);
      wordEl.classList.remove("is-paused");
      schedule(DELETE_MS, tick);
      return;
    }

    deleting = false;
    roleIndex = (roleIndex + 1) % roles.length;
    if (roleIndex === 0) {
      shuffleInPlace(roles);
    }
    syncArticle();
    wordEl.classList.remove("is-paused");
    schedule(TYPE_MS, tick);
  }

  syncArticle();
  schedule(TYPE_MS, tick);

  document.addEventListener("visibilitychange", function () {
    if (document.hidden && timerId !== null) {
      clearTimeout(timerId);
      timerId = null;
    } else if (!document.hidden && timerId === null) {
      schedule(HOLD_MS, tick);
    }
  });
})();
