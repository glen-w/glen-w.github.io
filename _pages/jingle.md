---
layout: page
title: jingle
permalink: /jingle/
---

<div style="text-align: center; margin: 2rem 0;">
  <img 
    id="crossword-button" 
    src="{{ '/assets/img/misc/crossword_button.png' | relative_url }}" 
    alt="Crossword Button" 
    style="cursor: pointer; max-width: 100%; height: auto;"
  />
</div>

<audio id="jingle-audio" preload="auto">
  <source src="{{ '/assets/audio/jingle.mp3' | relative_url }}" type="audio/mpeg">
</audio>

<script>
  document.addEventListener('DOMContentLoaded', function() {
    const button = document.getElementById('crossword-button');
    const audio = document.getElementById('jingle-audio');
    
    if (button && audio) {
      button.addEventListener('click', function() {
        audio.play().catch(function(error) {
          console.log('Audio play failed:', error);
        });
      });
    }
  });
</script>
