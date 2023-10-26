function evaluateEnemy() {
    document.getElementById("output").textContent = "You said: " + document.getElementById("creatureInput").value;
    getEnemyInfo(document.getElementById("creatureInput").value, "weight")
}

function compareNames() {
    var input = document.getElementById("creatureInput").value;
    $.getJSON('creatureData.json', function(data) {
        $.each(data.creature, function(i, c) {
            if (input == c.name) {
                document.getElementById("output").textContent = c.weight
            }
        });
    });
}

function getEnemyInfo(creature, elem) {
    console.log("hi!")
}
