
let loop = 0;
let actions = [];
let zones = [];
let currentStory = [];

function nextLoop() {
    loop++;
    document.getElementById('loopDisplay').textContent = "Loop: " + loop;
    if (loop in storyTriggers) {
        const storyKey = storyTriggers[loop];
        unlockStory(storyKey);
    }
}

function unlockStory(key) {
    const storyText = storyDatabase[key];
    if (storyText) {
        currentStory.push(storyText);
        updateStoryBox();
    }
}

function updateStoryBox() {
    document.getElementById('storyBox').innerHTML = currentStory.map(s => "<p>" + s + "</p>").join("");
}

window.onload = () => {
    document.getElementById("zoneDisplay").innerHTML = zones.map(z => "<div>" + z.name + "</div>").join("");
    document.getElementById("actionPanel").innerHTML = actions.map(a => "<button onclick='" + a.onClick + "'>" + a.name + "</button>").join("");
}
