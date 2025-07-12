
import { TASKS } from './constants.js';
import { BASE_XP_GAIN, MAX_XP, SILL_REGEN_RATE, GEL_GAIN_RATE } from './config.js';

let stats = {
  sill: 100,
  gel: 0,
  focus: 0,
  xp: {
    cart: 0,
    rock: 0,
    tunnel: 0,
    shift: 0,
    focus: 0,
  },
};

let autoUpdate = true;

function gainXP(task) {
  if (stats.sill <= 0) return;
  stats.xp[task] += BASE_XP_GAIN;
  if (stats.xp[task] > MAX_XP) stats.xp[task] = MAX_XP;
  stats.sill -= 1;
  stats.gel += GEL_GAIN_RATE;
  stats.focus += task === 'focus' ? 1 : 0;
  if (autoUpdate) updateUI();
}

function updateUI() {
  document.getElementById('sill').textContent = stats.sill;
  document.getElementById('gel').textContent = stats.gel;
  document.getElementById('focus').textContent = stats.focus;

  TASKS.forEach(task => {
    const value = stats.xp[task];
    const fill = document.getElementById(`xp-${task}`);
    const text = document.getElementById(`xp-${task}-text`);
    if (fill) fill.style.width = (value / MAX_XP) * 100 + '%';
    if (text) text.textContent = `${value} XP`;
  });
}

function completeChapter7() {
  logEvent("Chapter 7 completed.");
  if (autoUpdate) updateUI();
}


function getPlayerStats(playerXP) {
  const strengthXP = playerXP.cart;
  const speedXP = playerXP.rock;
  const defenseXP = playerXP.tunnel;
  const enduranceXP = playerXP.shift;
  const focusXP = playerXP.focus;

  return {
    atk: Math.floor(strengthXP / 10 + speedXP / 20),
    def: Math.floor(defenseXP / 15),
    hp: Math.floor(enduranceXP / 10),
    critChance: Math.min(100, Math.floor(focusXP / 25)),
    dodgeChance: Math.min(50, Math.floor(speedXP / 20)),
  };
}

function fightBoss() {
  logEvent("You challenged the Valking Captain...");
  if (autoUpdate) updateUI();
}

function logEvent(text) {
  const log = document.getElementById('event-log');
  const entry = document.createElement('div');
  entry.textContent = `[Event] ${text}`;
  log.appendChild(entry);
  log.scrollTop = log.scrollHeight;
}

window.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("toggle-auto-update");
  if (toggle) {
    toggle.textContent = autoUpdate ? "Disable Auto-Update" : "Enable Auto-Update";
    toggle.addEventListener("click", () => {
      autoUpdate = !autoUpdate;
      toggle.textContent = autoUpdate ? "Disable Auto-Update" : "Enable Auto-Update";
    });
  }

  const refresh = document.getElementById("refresh-ui");
  if (refresh) {
    refresh.addEventListener("click", updateUI);
  }

  updateUI(); // Initial load
});

// Export to actions.js
export { gainXP, completeChapter7, fightBoss };



// === IDLE LOOP ===
// Passive XP gain and stamina regen

function idleTick() {
  if (!idleEnabled) return;

  const passiveXP = 1;
  const regenRate = 1;

  for (let task in playerXP) {
    playerXP[task] += passiveXP;
    animateXPGain(task); // Highlight bar
  }

  sill = Math.min(100, sill + regenRate);
  updateUI();
});



function animateXPGain(task) {
  const bar = document.getElementById(`xp-${task}`);
  if (!bar) return;

  bar.style.transition = 'none';
  bar.style.backgroundColor = '#00ff99';

  setTimeout(() => {
    bar.style.transition = 'background-color 0.5s ease';
    bar.style.backgroundColor = '#8e44ad';
  }, 100);
}



function animateSillRegen() {
  const sillElem = document.getElementById("sill");
  if (!sillElem) return;

  sillElem.style.transition = 'color 0s';
  sillElem.style.color = '#00ffcc';

  setTimeout(() => {
    sillElem.style.transition = 'color 0.5s ease';
    sillElem.style.color = '#eee';
  }, 100);
}
