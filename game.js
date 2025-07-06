<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Echoform Idle</title>
  <style>
    body { font-family: sans-serif; padding: 20px; background-color: #111; color: #eee; }
    #stats, #tasks, #monsters, #log { margin-bottom: 20px; }
    button { margin: 4px; padding: 8px 12px; background: #444; color: #fff; border: none; border-radius: 4px; }
    .stat-line { margin: 2px 0; }
    .xp-line { font-size: 0.85em; color: #aaa; }
    button[title] { position: relative; }
    button[title]:hover::after {
      content: attr(title);
      position: absolute;
      background: #222;
      color: #eee;
      padding: 6px;
      border-radius: 4px;
      top: 100%;
      left: 0;
      white-space: pre-wrap;
      z-index: 10;
    }
  </style>
</head>
<body>
  <h1>Echoform: Astral Awakening</h1>

  <div id="stats">
    <h2>Stats</h2>
    <div class="stat-line">Sill: <span id="sill">0</span></div>
    <div class="stat-line">Gel-Essence: <span id="gel">0</span></div>
    <div class="stat-line">Strength: <span id="stat-strength">0</span></div>
    <div class="stat-line">Defense: <span id="stat-defense">0</span></div>
    <div class="stat-line">Endurance: <span id="stat-endurance">0</span></div>
    <div class="stat-line">Focus: <span id="stat-focus">0</span></div>
    <div class="stat-line">Attack: <span id="stat-attack">0</span></div>
    <div class="stat-line">Traits: <span id="traits">None</span></div>
  </div>

  <div id="tasks">
    <h2>Mining Tasks</h2>
    <button id="cart" title="Strength + Gel: Move heavy ore carts from shaft to stockpile\nEchoes whisper that these carts once bore relics of the Forgotten War.">Push Ore Cart</button><span class="xp-line" id="xp-cart"> XP: 0</span><br />
    <button id="rock" title="Strength: Break smaller rocks into gravel using hand tools\nSome say the shattered stones still remember ancient footsteps.">Break Rocks</button><span class="xp-line" id="xp-rock"> XP: 0</span><br />
    <button id="tunnel" title="Endurance: Dig longer tunnels through compact earth\nMiners speak of voices buried deep beneath the roots of the world.">Dig Tunnel</button><span class="xp-line" id="xp-tunnel"> XP: 0</span><br />
    <button id="shift" title="Endurance + Strength: Simulate prolonged labor under pressure\nEvery swing echoes the toil of ancestors bound by Gel-touched chains.">End Shift</button><span class="xp-line" id="xp-shift"> XP: 0</span><br />
    <button id="focus" title="Focus: Channel clarity to detect rare materials more easily\nIt is said only those attuned to Gel Essence can see the shimmer of frost ore.">Mindful Mining</button><span class="xp-line" id="xp-focus"> XP: 0</span>
  </div>

  <div id="monsters">
    <h2>Monster Hunts</h2>
    <button id="boar" title="Strength + Attack: Charge and clash with wild boars\nOnce guardians of the hills, these beasts now roam untamed by Viking hand.">Wild Boar</button><span class="xp-line" id="xp-boar"> XP: 0</span><br />
    <button id="elk" title="Endurance: Outlast a powerful mountain elk in the wild\nElk antlers were once carved into focus charms for Gel-born seers.">Mountain Elk</button><span class="xp-line" id="xp-elk"> XP: 0</span><br />
    <button id="wolf" title="Defense + Strength: Survive coordinated attacks from wolves\nLone wolves are feared, for some carry the gleam of ancient intelligence.">Lone Wolf</button><span class="xp-line" id="xp-wolf"> XP: 0</span><br />
    <button id="lynx" title="Focus + Defense: React to sudden strikes in tight terrain\nLegends say Silent Lynxes were once familiars of the frozen mystics.">Silent Lynx</button><span class="xp-line" id="xp-lynx"> XP: 0</span><br />
    <button id="bear" title="All Stats: Survive and slay a giant bear\nGiant Bears sleep on relics buried beneath ancient roots — few return from their dens.">Giant Bear</button><span class="xp-line" id="xp-bear"> XP: 0</span>
  </div>

  <button id="fight-boss" style="display:none">Fight Valking Captain</button>
  <button id="complete-ch7">Complete Chapter 7</button>

  <div id="log">
    <h2>Combat Log</h2>
    <div id="combat-log" style="height:150px; overflow-y:auto; border:1px solid #555; padding:10px;"></div>
  </div>

  <script type="module" src="game.js"></script>
</body>
</html>
