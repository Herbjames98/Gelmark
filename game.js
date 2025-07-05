document.addEventListener("DOMContentLoaded", () => {
  const panels = {
    stats: `
      <div class="gauge-box">
        <label>Health</label>
        <div class="gauge health">
          <div class="fill" id="health-bar"></div>
          <span class="gauge-label" id="health-text">0</span>
        </div>
      </div>
      <div class="gauge-box">
        <label>Defense</label>
        <div class="gauge defense">
          <div class="fill" id="defense-bar"></div>
          <span class="gauge-label" id="defense-text">0</span>
        </div>
      </div>
      <div class="gauge-box">
        <label>Energy</label>
        <div class="gauge energy">
          <div class="fill" id="energy-bar"></div>
          <span class="gauge-label" id="energy-text">0</span>
        </div>
      </div>
    `,
    skills: `
      <div class="skill-box"><strong>Heal</strong><button onclick="alert('You used Heal!')">Use</button></div>
    `
  };

  const buttons = document.querySelectorAll(".character-tab-btn");
  const contentArea = document.getElementById("character-content");

  buttons.forEach(btn => {
    btn.addEventListener("click", () => {
      const target = btn.dataset.target;
      contentArea.innerHTML = panels[target] || "<p>Coming soon...</p>";
      updateBars();
    });
  });

  document.querySelector(".character-tab-btn[data-target='stats']")?.click();

  const focusDisplay = document.getElementById("focus-display");
  let focus = 0;
  const maxFocus = 100;

  setInterval(() => {
    if (focus < maxFocus) {
      focus++;
      focusDisplay.textContent = `Focus: ${focus} / ${maxFocus}`;
    }
  }, 2000);

  // Bars
  let health = 1, defense = 1, energy = 1;
  const maxStat = 100;

  const updateBars = () => {
    const h = document.getElementById("health-bar");
    const d = document.getElementById("defense-bar");
    const e = document.getElementById("energy-bar");
    const ht = document.getElementById("health-text");
    const dt = document.getElementById("defense-text");
    const et = document.getElementById("energy-text");

    if (h) h.style.width = `${(health / maxStat) * 100}%`;
    if (d) d.style.width = `${(defense / maxStat) * 100}%`;
    if (e) e.style.width = `${(energy / maxStat) * 100}%`;

    if (ht) ht.textContent = health;
    if (dt) dt.textContent = defense;
    if (et) et.textContent = energy;
  };

  setInterval(() => {
    if (health < maxStat) health += 10;
    if (defense < maxStat) defense += 10;
    if (energy < maxStat) energy += 10;

    if (health > maxStat) health = maxStat;
    if (defense > maxStat) defense = maxStat;
    if (energy > maxStat) energy = maxStat;

    updateBars();
  }, 1000);

  // Locations
  const adventureButtons = document.querySelectorAll(".adventure-tab-btn");
  const adventureContent = document.getElementById("adventure-content");

  const fetchLocations = async () => {
    const allLocations = [
      { name: "Gælheim (Home of Gel)", unlocked: true },
      { name: "Nova Terra", unlocked: false },
      { name: "Zenthar", unlocked: false },
      { name: "Abyssal Gate", unlocked: false },
      { name: "Chronos Core", unlocked: false }
    ];

    let menu = `<div class="worlds-wrapper"><div class="worlds-scroll">`;

    allLocations.forEach((loc, index) => {
      const displayName = loc.unlocked ? loc.name : "???";
      const lockClass = loc.unlocked ? "" : "locked";
      menu += `<button class="world-button ${lockClass}" data-world-index="${index}">${displayName}</button>`;
    });

    menu += `</div><div id="world-detail" class="world-detail">Select a location to explore.</div></div>`;
    return menu;
  };

  adventureButtons.forEach(btn => {
    btn.addEventListener("click", async () => {
      if (btn.dataset.target === "locations") {
        const html = await fetchLocations();
        adventureContent.innerHTML = html;

        const worldBtns = document.querySelectorAll(".world-button:not(.locked)");
        const worldDetail = document.getElementById("world-detail");

        worldBtns.forEach(btn => {
          btn.addEventListener("click", () => {
            const worldName = btn.textContent;
            if (worldName.includes("Gælheim")) {
              worldDetail.innerHTML = `
                <h3>🌍 ${worldName}</h3>
                <p>Welcome to ${worldName}, where your journey begins.</p>
                <button onclick="alert('Gælheim action: tester')">tester</button>
              `;
            }
          });
        });
      }
    });
  });
});
