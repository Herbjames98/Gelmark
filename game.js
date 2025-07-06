// game.js

let stats = {
  sill: 100,
  maxSill: 100,
  gel: 50,
  focus: 0,
  xp: {
    cart: 0,
    rock: 0,
    tunnel: 0,
    shift: 0,
    focus: 0
  }
};

function gainXP(task, amount) {
  if (!stats.xp[task]) stats.xp[task] = 0;
  stats.xp[task] += amount;
  stats.focus += Math.floor(amount / 5); // Each gain slightly builds focus
  updateUI();
}

function updateUI() {
  document.getElementById("sill").textContent = stats.sill;
  document.getElementById("gel").textContent = stats.gel;
  document.getElementById("focus").textContent = stats.focus;

  for (const task in stats.xp) {
    const xpValue = Math.min(stats.xp[task], 100);
    const bar = document.getElementById("xp-" + task);
    if (bar) bar.style.width = xpValue + "%";
  }
}

function completeChapter7() {
  alert("Chapter 7 complete. Rumors spread… A powerful figure approaches.");
}

function fightBoss() {
  alert("You confront the Valking Captain. Prepare for the battle of your life!");
}
