import { tasks, monsters } from './actions.js';

let sill = 100;
let gel = 0;
let traits = new Set();
let activeTask = null;
let taskTimer = 0;
let lastActionTime = Date.now();

let stats = {
  Strength: 0,
  Defense: 0,
  Endurance: 0,
  Focus: 0,
  Attack: 0
};

let taskXP = {};
Object.keys(tasks).forEach(id => taskXP[id] = 0);

let monsterKillCount = 0;

let chapterProgress = {
  ch7: false,
  bossDefeated: false
};

const sillDisplay = document.getElementById("sill");
const gelDisplay = document.getElementById("gel");
const traitsDisplay = document.getElementById("traits");
const log = document.getElementById("combat-log");
const bossButton = document.getElementById("fight-boss") || createBossButton();
const completeCh7Button = document.getElementById("complete-ch7") || createCh7Button();

function createBossButton() {
  const button = document.createElement("button");
  button.id = "fight-boss";
  button.textContent = "Fight Valking Captain";
  document.body.appendChild(button);
  return button;
}

function createCh7Button() {
  const button = document.createElement("button");
  button.id = "complete-ch7";
  button.textContent = "Complete Chapter 7";
  document.body.appendChild(button);
  return button;
}

function logMessage(msg) {
  const p = document.createElement("div");
  p.textContent = msg;
  log.appendChild(p);
  log.scrollTop = log.scrollHeight;
}

function updateUI() {
  sillDisplay.textContent = Math.floor(sill);
  gelDisplay.textContent = gel;
  traitsDisplay.textContent = [...traits].join(", ") || "None";
  bossButton.style.display = chapterProgress.ch7 && !chapterProgress.bossDefeated ? "block" : "none";

  for (let stat in stats) {
    const el = document.getElementById("stat-" + stat.toLowerCase());
    if (el) el.textContent = stats[stat];
  }
}

function regenSill() {
  const now = Date.now();
  const delta = (now - lastActionTime) / 1000;
  lastActionTime = now;
  const missing = 100 - sill;
  if (missing > 0) {
    sill += Math.min(missing, 0.5 * delta);
  }
}

function gainXP(taskId) {
  taskXP[taskId]++;
  if (Object.values(taskXP).filter(x => x > 0).length >= 3) {
    traits.add("Veteran Echo");
  }
}

function completeTask(task) {
  if (task.reward) {
    stats[task.reward.stat] += 1;
    gel += task.reward.gel;
    monsterKillCount++;
    logMessage(`Defeated ${task.name}, gained ${task.reward.stat} and +${task.reward.gel} Gel.`);
    if (monsterKillCount >= 10) traits.add("Iron Pulse");
  } else {
    stats[task.stat] += 1;
    gainXP(task.id);
    logMessage(`Completed ${task.name}, +1 ${task.stat}.`);
  }
  updateUI();
}

function startTask(task) {
  if (sill < task.sillCost || activeTask) return;
  sill -= task.sillCost;
  activeTask = task;
  taskTimer = task.duration;
  logMessage(`Started ${task.name}...`);
  updateUI();
}

function gameLoop() {
  regenSill();
  if (activeTask) {
    taskTimer -= 1;
    if (taskTimer <= 0) {
      completeTask(activeTask);
      activeTask = null;
    }
  }
  updateUI();
}

["cart", "rock", "tunnel", "shift", "focus"].forEach(id => {
  const el = document.getElementById(id);
  if (el) el.onclick = () => startTask({ ...tasks[id], id });
});

["boar", "elk", "wolf", "lynx", "bear"].forEach(id => {
  const el = document.getElementById(id);
  if (el) el.onclick = () => startTask(monsters[id]);
});

if (bossButton) {
  bossButton.onclick = () => {
    if (sill < 30 || gel < 50) {
      logMessage("You're not ready to face the Valking Captain.");
      return;
    }
    sill -= 30;
    logMessage("Engaged in the duel with the Valking Captain...");
    setTimeout(() => {
      traits.add("Loopborn");
      chapterProgress.bossDefeated = true;
      logMessage("Victory! G.R.A.C.E. fully reawakens. Act 3 unlocked.");
      updateUI();
    }, 2000);
  };
}

if (completeCh7Button) {
  completeCh7Button.onclick = () => {
    chapterProgress.ch7 = true;
    logMessage("Chapter 7 completed. The Valking Captain senses your growth...");
    updateUI();
  };
}

setInterval(gameLoop, 1000);
updateUI();
