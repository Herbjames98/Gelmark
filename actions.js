// actions.js
import { TASKS } from './constants.js'; // Externalized task names

// Generalized handler to debounce task clicks
function handleTaskClick(task, btn) {
  btn.disabled = true;
  gainXP(task);
  setTimeout(() => {
    btn.disabled = false;
  }, 300);
}

document.addEventListener("DOMContentLoaded", () => {
  if (typeof gainXP !== "function" || typeof completeChapter7 !== "function" || typeof fightBoss !== "function") {
    console.error("Required game logic functions are not defined. Check game.js loading.");
    return;
  }

  TASKS.forEach(task => {
    const btn = document.getElementById(`task-${task}`);
    if (btn) {
      btn.addEventListener("click", () => handleTaskClick(task, btn));
    } else {
      console.warn(`Button for task '${task}' not found.`);
    }
  });

  const ch7 = document.getElementById("complete-ch7");
  if (ch7) {
    ch7.addEventListener("click", completeChapter7);
  } else {
    console.warn("Chapter 7 completion button not found.");
  }

  const bossBtn = document.getElementById("fight-boss");
  if (bossBtn) {
    bossBtn.addEventListener("click", fightBoss);
  } else {
    console.warn("Boss fight button not found.");
  }
});
