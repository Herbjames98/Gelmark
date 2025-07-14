// Initialize stats
const stats = {
    strength: 0,
    speed: 0,
    defense: 0,
    endurance: 0,
    focus: 0,
    gel: 0
};

// Update UI
function updateUI() {
    for (let stat in stats) {
        document.getElementById(stat).textContent = stats[stat];
    }
}

// Train a stat manually
function train(stat) {
    if (stats.hasOwnProperty(stat)) {
        stats[stat]++;
        updateUI();
    }
}

// Passive gel generation every 5 seconds
setInterval(() => {
    if (stats.focus >= 5) {
        stats.gel += 1;
        updateUI();
    }
}, 5000);

// Initial draw
updateUI();
