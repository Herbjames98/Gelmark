
let focusAvailable = 100;
let stats = { str: 0, spd: 0, ki: 0 };
let assigned = { str: 0, spd: 0, ki: 0 };

function updateDisplay() {
    document.getElementById("focusCount").textContent = focusAvailable;
    document.getElementById("strStat").textContent = stats.str;
    document.getElementById("spdStat").textContent = stats.spd;
    document.getElementById("kiStat").textContent = stats.ki;
}

function assignProjections() {
    let strVal = parseInt(document.getElementById("strInput").value) || 0;
    let spdVal = parseInt(document.getElementById("spdInput").value) || 0;
    let kiVal = parseInt(document.getElementById("kiInput").value) || 0;
    let total = strVal + spdVal + kiVal;

    if (total > focusAvailable) {
        alert("Not enough focus!");
        return;
    }

    assigned = { str: strVal, spd: spdVal, ki: kiVal };
    focusAvailable -= total;
    updateDisplay();
}

function trainingTick() {
    stats.str += assigned.str;
    stats.spd += assigned.spd;
    stats.ki += assigned.ki;
    updateDisplay();
}

setInterval(trainingTick, 1000);
window.onload = updateDisplay;
