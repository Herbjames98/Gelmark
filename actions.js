import { TASKS } from './constants.js';

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
  }

  const bossBtn = document.getElementById("fight-boss");
  if (bossBtn) {
    bossBtn.addEventListener("click", fightBoss);
  }
});