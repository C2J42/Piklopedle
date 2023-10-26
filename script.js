let targetCreature = null;
let inputCreature = null;

function evaluateInput() {
    document.getElementById("output").textContent = "You said: " + document.getElementById("creatureInput").value;
    getEnemyInfo(document.getElementById("creatureInput").value, compareVals)
    // maybe add new row per input, showing max 5-10 rows?
}

function getEnemyInfo(inputName, callback) {
    var foundTarg = false;
    $.getJSON('creatureData.json', function(data) {
        $.each(data.creature, function(i, c) {
            if (inputName == c.name) {
                document.getElementById("inputName").textContent = c.name;
                document.getElementById("inputWeight").textContent = c.weight;
                document.getElementById("inputFirstAppear").textContent = c.appearances.substring(1, 2);
                inputCreature = c
                foundTarg = true;
                callback();
                return;
            }
        });
        if (!foundTarg) {
            inputCreature = null;
            document.getElementById("inputName").textContent = "n/a";
            document.getElementById("inputWeight").textContent = "n/a";
            document.getElementById("inputFirstAppear").textContent = "n/a";
            callback();
        }
    });
}

function newTarget() {
    $.getJSON('creatureData.json', function(data) {
        var keys = Object.keys(data.creature)
        var randKey = keys[Math.floor(Math.random() * keys.length)]
        targetCreature = data.creature[randKey]
        console.log(targetCreature)
    });
}

function compareVals() {
    if (inputCreature != null) {
        // compare name
        document.getElementById("targetNameCompare").textContent = inputCreature.name == targetCreature.name;
        // compare weight
        document.getElementById("targetWeightCompare").textContent = inputCreature.weight == targetCreature.weight;
        // compare first appear
        document.getElementById("targetFirstAppearCompare").textContent = inputCreature.appearances.substring(1, 2) == targetCreature.appearances.substring(1, 2);
    } else {
        document.getElementById("targetNameCompare").textContent = "n/a";
        // compare weight
        document.getElementById("targetWeightCompare").textContent = "n/a";
        // compare first appear
        document.getElementById("targetFirstAppearCompare").textContent = "n/a";
    }
}
