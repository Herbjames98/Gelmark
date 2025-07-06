// actions.js

window.addEventListener('DOMContentLoaded', function () {
  const fightBossBtn = document.getElementById("fight-boss");
  if (!fightBossBtn) {
    console.warn("Missing element with ID 'fight-boss'. Please ensure it exists in index.html.");
  } else {
    fightBossBtn.addEventListener("click", fightBoss);
  }

  const ch7Btn = document.getElementById("complete-ch7");
  if (!ch7Btn) {
    console.warn("Missing element with ID 'complete-ch7'. Please ensure it exists in index.html.");
  } else {
    ch7Btn.addEventListener("click", completeChapter7);
  }

  if (typeof gainXP !== 'function') {
    console.error("Function 'gainXP' is not defined. Ensure it exists in the global scope or in game.js.");
  }

  if (typeof tooltips !== 'object') {
    console.error("Object 'tooltips' is not defined. Ensure it exists and is properly populated before assigning tooltips.");
  }

  ['cart','rock','tunnel','shift','focus','boar','elk','wolf','lynx','bear'].forEach(task => {
    const el = document.getElementById(task);
    if (el) {
      el.addEventListener("click", () => gainXP(task, 10));
      el.title = tooltips && tooltips[task] ? tooltips[task] : "";
    } else {
      console.warn(`Missing element with ID '${task}'. Please ensure it exists in index.html.`);
    }
  });

  if (typeof updateUI !== 'function') {
    console.error("Function 'updateUI' is not defined. Ensure it exists in the global scope or in game.js.");
  } else {
    updateUI();
  }
});
