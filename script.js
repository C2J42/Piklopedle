function evaluateEnemy() {
    document.getElementById("output").textContent = "You said: " + document.getElementById("creatureInput").value;
    getEnemyInfo(document.getElementById("creatureInput").value)
}

function compareNames() {
    const input = document.getElementById("creatureInput").value;
    $.getJSON('creatureData.json', function(data) {
        $.each(data.creature, function(i, c) {
            if (input == c.name) {
                document.getElementById("output").textContent = c.weight
            }
        });
    });
}

function getEnemyInfo(inputName) {
    $.getJSON('creatureData.json', function(data) {
        $.each(data.creature, function(i, c) {
            if (inputName == c.name) {
                document.getElementById("inputName").textContent = c.name;
                document.getElementById("inputWeight").textContent = c.weight;
                document.getElementById("inputFirstAppear").textContent = c.appearances.substring(1, 2);
                return;
            }
        });
    });
    document.getElementById("inputName").textContent = "n/a";
    document.getElementById("inputWeight").textContent = "n/a";
    document.getElementById("inputFirstAppear").textContent = "n/a";
}
