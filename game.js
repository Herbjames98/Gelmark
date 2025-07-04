
let loop = 0;
let power = 0;
let currentStory = [];
let queue = [];
let lastAction = null;

function updateDisplay() {
    document.getElementById('loopDisplay').textContent = "Loop: " + loop + " | Power: " + power;
    document.getElementById('zoneDisplay').innerHTML = zones.map(z => "<div>" + z.name + "</div>").join("");
    document.getElementById('actionPanel').innerHTML = actions.map((a, i) =>
        "<button onclick='queueAction(" + i + ")'>" + a.name + "</button>").join("");
    document.getElementById('queueBox').innerHTML = queue.map(a => "<div>" + a.name + "</div>").join("");
    document.getElementById('storyBox').innerHTML = currentStory.map(s => "<p>" + s + "</p>").join("");
}

function nextLoop() {
    loop++;
    if (loop in storyTriggers) {
        currentStory.push(storyDatabase[storyTriggers[loop]]);
    }
    updateDisplay();
}

function queueAction(i) {
    const action = actions[i];
    queue.push({...action});
    lastAction = {...action};
    processQueue();
    updateDisplay();
}

function repeatLast() {
    if (lastAction) {
        queue.push({...lastAction});
        processQueue();
        updateDisplay();
    }
}

function clearQueue() {
    queue = [];
    updateDisplay();
}

function processQueue() {
    if (queue.length === 0) return;
    const action = queue.shift();
    setTimeout(() => {
        power += action.powerGain || 0;
        currentStory.push(storyDatabase[action.storyKey]);
        updateDisplay();
        processQueue();
    }, action.duration);
}

window.onload = updateDisplay;
