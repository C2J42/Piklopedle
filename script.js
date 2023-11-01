/**enemy being searched for*/
let targetCreature = null;
/**most recent input enemy*/
let inputCreature = null;

/**bc copy/paste annoying*/
let downArrow = "↓ ";
/**bc copy/paste annoying*/
let upArrow = "↑ ";
/**bc copy/paste annoying*/
let checkMark = "☑ ";
/**bc copy/paste annoying*/
let xMark = "☒ ";

// redo how data shown. Comparision stuff on the input fields, not target fields

/**
 * Gets info from the input field and evaluates it.
 */
function evaluateInput() {
    document.getElementById("output").textContent = "You said: " + document.getElementById("creatureInput").value;
    getEnemyInfo(document.getElementById("creatureInput").value, addComparison)
}

/**
 * Gets the info of the input enemy
 * @param {string} inputName 
 * @param {function} callback 
 */
function getEnemyInfo(inputName, callback) {
    var foundTarg = false;
    $.getJSON('creatureData.json', function(data) {
        // change to binary search maybe?
        $.each(data.creature, function(i, c) {
            // if input is an enemy
            if (inputName.trim().toLowerCase() == c.name.toLowerCase()) {
                inputCreature = c;
                foundTarg = true;
                callback();
                return;
            }
        });
        // if input enemy does not exist
        if (!foundTarg) {
            return
        }
    });
}

/**
 * Changes enemy being searched for
 */
function newTarget() {
    $.getJSON('creatureData.json', function(data) {
        var keys = Object.keys(data.creature)
        var randKey = keys[Math.floor(Math.random() * keys.length)]
        targetCreature = data.creature[randKey]
        console.log(targetCreature)
    });
    //delete all but first row
    let temp = document.getElementById("comparisonTable").rows.length;
    for (let i = 1; i < temp; i++) {
        document.getElementById("comparisonTable").deleteRow(1)
    }
}

/**
 * Compares input values and target values
 */
function compareVals() {
    if (inputCreature != null) {
        // compare name
        if (inputCreature.name == targetCreature.name) {
            document.getElementById("targetNameCompare").textContent = targetCreature.name;
        }

        // compare weight
        let lormWeight = (parseInt(inputCreature.weight) > parseInt(targetCreature.weight) ? "less" 
        : (parseInt(inputCreature.weight) == parseInt(targetCreature.weight) ? "equal!" : "more"));
        document.getElementById("targetWeightCompare").textContent = lormWeight;

        // TODO compare health
        let lormHealth = (parseInt(inputCreature.health) > parseInt(targetCreature.health) ? "less" 
        : (parseInt(inputCreature.health) == parseInt(targetCreature.health) ? "equal!" : "more"));
        document.getElementById("targetHealthCompare").textContent = lormHealth;

        // compare family
        if (inputCreature.family == targetCreature.family) {
            document.getElementById("targetFamilyCompare").textContent = targetCreature.family;
        }

        // compare first appear
        document.getElementById("targetFirstAppearCompare").textContent = inputCreature.appearances.substring(1, 2) == targetCreature.appearances.substring(1, 2);
    } else {
        // compare name
        document.getElementById("targetNameCompare").textContent = "???";
        // compare weight
        document.getElementById("targetWeightCompare").textContent = "n/a";
        // compare health
        document.getElementById("targetHealthCompare").textContent = "n/a";
        // compare first appear
        document.getElementById("targetFirstAppearCompare").textContent = "n/a";
        // compare family
        document.getElementById("targetFamilyCompare").textContent = "n/a"
    }
}

/**
 * Adds most recent input to top of comparison table
 */
function addComparison() {
    let table = document.getElementById("comparisonTable");
    let row = table.insertRow(1);
    // name cell
    (inputCreature.name == targetCreature.name ? 
        row.insertCell(0).textContent = checkMark + inputCreature.name :
        row.insertCell(0).textContent = xMark + inputCreature.name);
    // weight cell
    (parseInt(inputCreature.weight) == parseInt(targetCreature.weight) ?
        row.insertCell(1).textContent = checkMark + inputCreature.weight:
        parseInt(inputCreature.weight) > parseInt(targetCreature.weight) ?
            row.insertCell(1).textContent = downArrow + inputCreature.weight :
            row.insertCell(1).textContent = upArrow + inputCreature.weight);
    // health cell
    (parseInt(inputCreature.health) == parseInt(targetCreature.health) ?
        row.insertCell(2).textContent = checkMark + inputCreature.health:
        parseInt(inputCreature.health) > parseInt(targetCreature.health) ?
            row.insertCell(2).textContent = downArrow + inputCreature.health :
            row.insertCell(2).textContent = upArrow + inputCreature.health);
    // firstAppear cell
    (inputCreature.appearances.substring(1, 2) == targetCreature.appearances.substring(1, 2) ? 
        row.insertCell(3).textContent = checkMark + inputCreature.appearances.substring(1, 2) :
        row.insertCell(3).textContent = xMark + inputCreature.appearances.substring(1, 2));
    // family cell
    (inputCreature.family == targetCreature.family ? 
        row.insertCell(4).textContent = checkMark + inputCreature.family :
        row.insertCell(4).textContent = xMark + inputCreature.family);
    // image cell
    //row.insertCell(5).textContent = "TODO: image";
    let img = document.createElement("img");
    img.src = inputCreature.imgUrl;
    img.height = 64;
    img.width = 64;
    try {
        row.insertCell(5).appendChild(img);
    } catch {
        img.src = "https://pikmin.wiki.gallery/images/5/5b/NSO_Icon_Pikmin_4_Wave_1_Character_7.jpg";
        // oatchi is default because he's the best boy
        row.insertCell(5).appendChild(img);
    }
}

function compareHelper() {
    
}
