

function evaluateEnemy() {
    console.log("hi!")
    document.getElementById("output").textContent = "You said: " + document.getElementById("creatureInput").value;
    getEnemyInfo(document.getElementById("creatureInput").value, "weight")
}

function getEnemyInfo(creature, elem) {
    var fr = new FileReader();
    output = JSON.parse(fr.readAsText("creatureData.json"));
    console.log(output);
    document.getElementById(elem).textContent = output;
}
