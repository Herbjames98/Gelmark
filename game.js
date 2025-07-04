
let loop = 0;
let actions = [];
let zones = [];
let currentStory = [];
let power = 0;
let queue = [];
let queueInterval = null;

function updateDisplay() {
    document.getElementById('loopDisplay').textContent = "Loop: " + loop + " | Power: " + power;
    document.getElementById('zoneDisplay').innerHTML = zones.map(z => "<div>" + z.name + "</div>").join("");
    document.getElementById('actionPanel').innerHTML = actions.map((a, i) =>
        "<button onclick='queueAction(" + i + ")'>" + a.name + "</button>").join("");
    updateStoryBox();
    updateQueueBox();
}

function nextLoop() {
    loop++;
    power += 5; // base power growth
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
    updateQueueBox();
    if (!queueInterval) {
        processQueue();
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
        queue.shift();
        updateDisplay();
        processQueue();
    }, countdown);
}

window.onload = () => {
    updateDisplay();
}
