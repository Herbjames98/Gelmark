// game.js
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
  if (task === 'focus') stats.focus += 1;
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

// Exported for actions.js
export { gainXP, completeChapter7, fightBoss };
