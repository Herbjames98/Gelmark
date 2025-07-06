// game.js

import { CONFIG } from './config.js';

let playerStats = {
  sill: 0,
  gel: 0,
  focus: 0,
  xp: {
    cart: 0,
    rock: 0,
    tunnel: 0,
    shift: 0,
    focus: 0
  },
  chapter: 6,
  bossDefeated: false
};

function gainXP(taskId) {
  if (!playerStats.xp.hasOwnProperty(taskId)) {
    console.warn(`Invalid task: '${taskId}'`);
    return;
  }

  updateResources(taskId);
  logTaskGain(taskId);
  updateUI();
}

function updateResources(taskId) {
  playerStats.xp[taskId] += CONFIG.XP_PER_TASK;
  playerStats.sill += CONFIG.SILL_GAIN_PER_XP;
  playerStats.gel = Math.max(0, playerStats.gel - CONFIG.GEL_DRAIN_PER_ACTION);
  if (taskId === 'focus') playerStats.focus += 1;
}

function logTaskGain(taskId) {
  logEvent(`You feel echoes stir as you train '${taskId}'.`);
}

function updateUI() {
  const statMap = ["sill", "gel", "focus"];
  statMap.forEach(stat => {
    const el = document.getElementById(stat);
    if (el) el.innerText = Math.floor(playerStats[stat]);
  });

  for (let task in playerStats.xp) {
    const xpVal = playerStats.xp[task];
    const fillPercent = Math.min(100, (xpVal / CONFIG.XP_TO_LEVEL) * 100);
    const fillElem = document.getElementById(`xp-${task}`);
    const textElem = document.getElementById(`xp-${task}-text`);
    if (fillElem) fillElem.style.width = `${fillPercent}%`;
    if (textElem) textElem.innerText = `${xpVal} XP`;
  }
}

function completeChapter7() {
  if (playerStats.chapter < 7) {
    playerStats.chapter = 7;
    logEvent("Chapter 7 completed. The air thickens with anticipation...");
  } else {
    logEvent("Chapter 7 is already complete.");
  }
  updateUI();
}

function fightBoss() {
  if (playerStats.chapter < 7) {
    logEvent("You must complete Chapter 7 first!");
    return;
  }
  if (playerStats.bossDefeated) {
    logEvent("You've already defeated the Valking Captain.");
    return;
  }
  if (playerStats.sill >= 100 && playerStats.focus >= 50) {
    playerStats.bossDefeated = true;
    logEvent("Victory! You have defeated the Valking Captain and entered Act 3.");
  } else {
    logEvent("You're not strong enough yet. Focus and Sill must rise.");
  }
  updateUI();
}

function logEvent(message) {
  const log = document.getElementById("event-log");
  if (log) {
    const entry = document.createElement("div");
    entry.textContent = message;
    log.appendChild(entry);
    log.scrollTop = log.scrollHeight;
  }
}

window.addEventListener("DOMContentLoaded", () => {
  const taskButtons = ["cart", "rock", "tunnel", "shift", "focus"];
  taskButtons.forEach(task => {
    const el = document.getElementById(`task-${task}`);
    if (el) {
      el.addEventListener("click", () => gainXP(task));
    }
  });

  const ch7 = document.getElementById("complete-ch7");
  if (ch7) ch7.addEventListener("click", completeChapter7);

  const boss = document.getElementById("fight-boss");
  if (boss) boss.addEventListener("click", fightBoss);

  updateUI();
});
