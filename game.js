
let loop = 0;
let actions = [];
let zones = [];
let currentStory = [];
let power = 0;
let queue = [];
let queueInterval = null;
let lastAction = null;

// Stats and skills
let stats = {
    strength: 0,
    speed: 0,
    intelligence: 0
};
let skills = {
    martialArts: 0,
    kiControl: 0
};

function updateDisplay() {
    document.getElementById('loopDisplay').textContent = "Loop: " + loop + " | Power: " + power;
    document.getElementById('zoneDisplay').innerHTML = zones.map(z => "<div>" + z.name + "</div>").join("");
    document.getElementById('actionPanel').innerHTML = actions.map((a, i) =>
        "<button onclick='queueAction(" + i + ")'>" + a.name + "</button>").join("");
    updateStoryBox();
    updateQueueBox();
    updateStatsUI();
}

function updateStatsUI() {
    document.getElementById('strBar').style.width = stats.strength + "%";
    document.getElementById('spdBar').style.width = stats.speed + "%";
    document.getElementById('intBar').style.width = stats.intelligence + "%";
    document.getElementById('martialBar').style.width = skills.martialArts + "%";
    document.getElementById('kiBar').style.width = skills.kiControl + "%";
}

function nextLoop() {
    loop++;
    power += 5;
    if (loop in storyTriggers) {
        const storyKey = storyTriggers[loop];
        unlockStory(storyKey);
    }
    updateDisplay();
}

function unlockStory(key) {
    const storyText = storyDatabase[key];
    if (storyText) {
        currentStory.push(storyText);
    }
}

function updateStoryBox() {
    document.getElementById('storyBox').innerHTML = currentStory.map(s => "<p>" + s + "</p>").join("");
}

function queueAction(index) {
    const action = actions[index];
    queue.push({...action});
    lastAction = {...action};
    updateQueueBox();
    if (!queueInterval) {
        processQueue();
    }
}

function clearQueue() {
    queue = [];
    updateQueueBox();
}

function repeatLast() {
    if (lastAction) {
        queue.push({...lastAction});
        updateQueueBox();
        if (!queueInterval) {
            processQueue();
        }
    }
}

function updateQueueBox() {
    const box = document.getElementById('queueBox');
    box.innerHTML = "<h3>Action Queue</h3>" + queue.map(a => "<div>" + a.name + "</div>").join("");
}

function processQueue() {
    if (queue.length === 0) {
        clearInterval(queueInterval);
        queueInterval = null;
        return;
    }

    const action = queue[0];
    document.getElementById('storyBox').innerHTML += "<p>Started: " + action.name + "</p>";
    let countdown = action.duration || 3000;

    setTimeout(() => {
        unlockStory(action.storyKey);
        power += action.powerGain || 0;

        // Apply stat/skill growth
        if (action.effects) {
            for (let stat in action.effects) {
                if (stats[stat] !== undefined) stats[stat] += action.effects[stat];
                if (skills[stat] !== undefined) skills[stat] += action.effects[stat];
            }
        }

        queue.shift();
        updateDisplay();
        processQueue();
    }, countdown);
}

window.onload = () => {
    updateDisplay();
}



let actionQueue = [];
let mana = 0;
let gold = 0;
let amount = 1;

function setAmount(val) {
    amount = val;
    document.getElementById("customAmount").value = val;
}

function updateAmount() {
    amount = parseInt(document.getElementById("customAmount").value) || 1;
}

function updateStats() {
    document.getElementById("mana").textContent = mana;
    document.getElementById("gold").textContent = gold;
}

function queueAction(action) {
    for (let i = 0; i < amount; i++) {
        if (document.getElementById("addToTop").checked) {
            actionQueue.unshift(action);
        } else {
            actionQueue.push(action);
        }
    }
    renderQueue();
}

function renderQueue() {
    const queueDiv = document.getElementById("queue");
    queueDiv.innerHTML = "";
    for (let act of actionQueue) {
        const div = document.createElement("div");
        div.textContent = act;
        queueDiv.appendChild(div);
    }
}

document.getElementById("customAmount").addEventListener("change", updateAmount);
document.getElementById("repeatLast").addEventListener("change", () => {});
document.getElementById("keepActive").addEventListener("change", () => {});
document.getElementById("addToTop").addEventListener("change", () => {});

function clearQueue() {
    actionQueue = [];
    renderQueue();
}

function nextLoop() {
    // Placeholder loop logic
    gold += 1;
    mana += 2;
    updateStats();
}
