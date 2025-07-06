// game.js

const stats = {
  sill: 50,
  gel: 0,
  strength: 0,
  defense: 0,
  endurance: 0,
  focus: 0,
  attack: 0
};

const xp = {
  cart: 0,
  rock: 0,
  tunnel: 0,
  shift: 0,
  focus: 0,
  boar: 0,
  elk: 0,
  wolf: 0,
  lynx: 0,
  bear: 0
};

const tooltips = {
  cart: "Push mining carts to build strength. 🛒 These were once used by the first miners to haul sacred ore.",
  rock: "Break rocks to develop brute strength. 🪨 Some say these stones remember the first war cry.",
  tunnel: "Dig tunnels to increase endurance. ⛏️ The echo of your strikes awakens the past.",
  shift: "Haul shifts underground to build resilience. 💪 The shifts blur into ritual over time.",
  focus: "Train stillness and concentration. 🧘 Only those who master silence hear G.R.A.C.E. whisper.",
  boar: "Hunt boars to hone your instincts. 🐗 Their tusks once crowned the clan's champions.",
  elk: "Track elk to improve endurance. 🦌 The chase teaches patience and breath.",
  wolf: "Confront wolves to sharpen your defense. 🐺 Steel your body as they test your perimeter.",
  lynx: "Face lynx to enhance precision. 🐈 Their gaze unnerves the untrained.",
  bear: "Challenge bears to prove your might. 🐻 Ancient spirits smile on those who endure.",
  strength: "Your raw physical force. 💪 Strength lets Echoforms carry heavier burdens and strike harder in combat.",
  defense: "The ability to withstand blows. 🛡️ Defense determines how much damage your Echoform can absorb before breaking.",
  endurance: "Your lasting power. 🏃‍♂️ Endurance governs your stamina in prolonged tasks and monster fights.",
  focus: "Clarity of mind. 🧠 Focus unlocks G.R.A.C.E. upgrades and hastens crafting insights.",
  attack: "Battle effectiveness. ⚔️ A higher attack stat increases your damage in fights, especially against elite foes.",
  sill: "Sill is your inner astral force. 🌌 It's the energy your Echoforms draw from the Essence Gel.",
  gel: "Gel-Essence is your active resource. 💧 It's spent when Echoforms act and recharges slowly over time."
};

function updateUI() {
  for (let key in stats) {
    const val = stats[key];
    document.getElementById(key === 'gel' ? 'gel' : key === 'sill' ? 'sill' : `stat-${key}`).textContent = val;
    document.getElementById(`bar-${key}`).style.width = `${Math.min(val / 100 * 100, 100)}%`;
    const statElement = document.getElementById(`stat-${key}`);
    if (statElement) statElement.title = tooltips[key];
  }
  for (let key in xp) {
    const val = xp[key];
    document.getElementById(`xp-${key}`).textContent = `XP: ${val}`;
    document.getElementById(`bar-xp-${key}`).style.width = `${Math.min(val / 100 * 100, 100)}%`;
  }
}

function gainXP(task, amount) {
  xp[task] += amount;
  switch(task) {
    case 'cart':
      stats.strength += 1;
      stats.gel += 1;
      break;
    case 'rock':
      stats.strength += 2;
      break;
    case 'tunnel':
      stats.endurance += 2;
      break;
    case 'shift':
      stats.endurance += 1;
      stats.strength += 1;
      break;
    case 'focus':
      stats.focus += 2;
      break;
    case 'boar':
      stats.strength += 1;
      stats.attack += 1;
      break;
    case 'elk':
      stats.endurance += 2;
      break;
    case 'wolf':
      stats.defense += 2;
      stats.strength += 1;
      break;
    case 'lynx':
      stats.defense += 1;
      stats.focus += 2;
      break;
    case 'bear':
      stats.strength += 1;
      stats.endurance += 1;
      stats.defense += 1;
      stats.focus += 1;
      stats.attack += 1;
      break;
  }
  updateUI(); // Re-render UI to reflect new XP, stats, and tooltips.
  checkUnlocks();
}

function checkUnlocks() {
  const totalPower = stats.strength + stats.defense + stats.endurance + stats.focus + stats.attack;
  if (totalPower >= 100) {
    const bossBtn = document.getElementById('fight-boss');
    if (bossBtn) bossBtn.style.display = 'inline-block';
  }
}

function logCombat(text) {
  const log = document.getElementById("combat-log");
  log.innerHTML += `<div>${text}</div>`;
  log.scrollTop = log.scrollHeight;
}

function fightBoss() {
  const success = stats.attack >= 20 && stats.endurance >= 15 && stats.defense >= 15;
  logCombat(success ? "You have defeated the Valking Captain." : "You were not strong enough.");
}

function completeChapter7() {
  logCombat("You feel a tension rising... a powerful figure is coming.");
}

const fightBossBtn = document.getElementById("fight-boss");
if (fightBossBtn) fightBossBtn.addEventListener("click", fightBoss);

const ch7Btn = document.getElementById("complete-ch7");
if (ch7Btn) ch7Btn.addEventListener("click", completeChapter7);

['cart','rock','tunnel','shift','focus','boar','elk','wolf','lynx','bear'].forEach(task => {
  const el = document.getElementById(task);
  if (el) {
    el.addEventListener("click", () => gainXP(task, 10));
    el.title = tooltips[task];
  }
});

updateUI();
