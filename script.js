/**enemy being searched for*/
let targetCreature = null;
/**most recent input enemy*/
let inputCreature = null;
/**true if target hasn't been found*/
let gameRunning = true;
/**true if daily mode*/
let dailyMode = true;

/**The thing to copy and send*/
let copyString = "";

/**bc copy/paste annoying*/
let downArrow = "↓ ";
/**bc copy/paste annoying*/
let upArrow = "↑ ";
/**bc copy/paste annoying*/
let checkMark = "☑ ";
/**bc copy/paste annoying*/
let xMark = "☒ ";

/**
 * Function run on page load
 */
function onLoad() {
    dailyTarget();
    setCreatureList();
    let dayStr = "make whatever day it is mm/dd bc THIS IS MURICA"
    let today = new Date();
    dayStr = (today.getMonth() + 1).toString() + "/" + today.getDate();
    copyString = "Piklopedle " + dayStr + "<br>";

    // making sure vars resent
    inputCreature = null;
    gameRunning = true;
    dailyMode = true;
}

/**
 * calls evaluateInput() if enter key pressed
 */
document.addEventListener('keydown', function(event) {
    if (event.key == "Enter") {
        evaluateInput();
    }
});

/**
 * Gets info from the input field and evaluates it.
 */
function evaluateInput() {
    if (gameRunning) {
        getEnemyInfo(document.getElementById("creatureInput").value, addComparison)
    }
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
                document.getElementById("invalidInputWarning").textContent = "";
                document.getElementById("creatureInput").value = "";
                return;
            }
        });
        // if input enemy does not exist
        if (!foundTarg) {
            let temp = document.getElementById("creatureInput").value;
            if (temp.trim() != "") {
                document.getElementById("invalidInputWarning").textContent = 
                    "\"" + temp + "\" is not a valid input";
            }
            document.getElementById("creatureInput").value = "";
            return;
        }
    });
}

/**
 * Changes enemy being searched for
 */
function newTarget() {
    $.getJSON('creatureData.json', function(data) {
        var keys = Object.keys(data.creature);
        var randKey = keys[Math.floor(Math.random() * keys.length)];
        targetCreature = data.creature[randKey];
        console.log(targetCreature);
    });
    //delete all but first row
    let temp = document.getElementById("comparisonTable").rows.length;
    for (let i = 1; i < temp; i++) {
        document.getElementById("comparisonTable").deleteRow(1);
    }
    gameRunning = true;
    document.getElementById("creatureInput").style.display = "inline";
    document.getElementById("enterButton").style.display = "inline";
    document.getElementById("freePlayButton").style.display = "none";
}

/**
 * Gets a random target enemy, using current day as a seed
 */
function dailyTarget() {
    // get day, make all days within 148 of each other equal (divison and Math.floor prob)
    let numKeys = 148;
    let today = new Date();
    let acDate = new Date("10/26/2001"); // arbitrary count date - release date of Pikmin 1
    let dayDiff = Math.floor((today.getTime()-acDate.getTime()) / (1000*3600*24));
    let index = Math.floor(dayDiff/numKeys);
    let seed = dayDiff % numKeys; // used as seed and target index
    // randomize list of numbers between [0, 148) using altered day as seed
    let numArr = [];
    for (let i = 0; i < numKeys; i++) {
        numArr[i] = i;
    }
    //   this ensures that all creatures are looped through before repitions occur
    numArr = shuffle(numArr, seed);

    // target is creatureData[dayDiff]
    $.getJSON('creatureData.json', function(data) {
        var keys = Object.keys(data.creature);
        var randKey = keys[numArr[index]];
        targetCreature = data.creature[randKey];
        console.log(targetCreature);
    });

    document.getElementById("freePlayButton").style.display = "none";
    // check that the day thing working correctly for periods of 148 days
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
    addToCopyStr();
    if (inputCreature.name == targetCreature.name) {
        doWin();
    }
}

/**
 * Helper for addComparison() that adds to the copy string
 */
function addToCopyStr() {
    let temp = "";
    if (dailyMode) {
        let row = document.getElementById("comparisonTable").rows[1];
        for (let i = 1; i <= 4; i++) {
            temp += row.cells[i].textContent.substring(0, 1);
        }
    }
    copyString += temp + "<br>";
}

/**
 * Things to happen when target matches input
 */
function doWin() {
    // basic stuff
    document.getElementById("eodThemeP4").play();
    gameRunning = false;
    document.getElementById("creatureInput").style.display = "none";
    document.getElementById("enterButton").style.display = "none";
    document.getElementById("freePlayButton").style.display = "inline";
    document.getElementById("winModal").style.display = "block";

    // add copyString to win modal (& get rid of trailing whitespace)
    if (dailyMode) {
        copyString = copyString.trim();
        document.getElementById("winModalText").innerHTML = "You won!<br>" + copyString;
        dailyMode = false;
    } else {
        document.getElementById("copyStrButton").style.display = "none";
        document.getElementById("winModalText").innerHTML = "You won!";
    }
}

/**
 * closes the win modal
 */
function closeWinModal() {
    document.getElementById("winModal").style.display = "none";
}

/**
 * Array shuffler.
 * From https://stackoverflow.com/questions/16801687/javascript-random-ordering-with-seed
 * @param {*} array array to shuffle.
 * @returns shuffled array
 */
function shuffle(array, seed) {
    var m = array.length, t, i;

    // While there remain elements to shuffle…
    while (m) {

        // Pick a remaining element…
        i = Math.floor(random(seed) * m--);

        // And swap it with the current element.
        t = array[m];
        array[m] = array[i];
        array[i] = t;
        ++seed
    }
    return array;
}

/**
 * "Random" number generator to help with shuffler
 * From https://stackoverflow.com/questions/16801687/javascript-random-ordering-with-seed
 * @param {*} seed
 * @returns "random" number
 */
function random(seed) {
    var x = Math.sin(seed++) * 10000; 
    return x - Math.floor(x);
}

/**
 * Sets up the datalist creatureList for autocomplete
 */
function setCreatureList() {
    let dl = document.getElementById("creatureList");
    $.getJSON('creatureData.json', function(data) {
        for (let i = 0; i < data.creature.length; i++) {
            let option = document.createElement("option");
            option.value = data.creature[i].name;
            dl.appendChild(option);
            //console.log(c.name);
        }
    });
}

function copyStrToClipboard() {
    //copyString.replace("<br>", "\n");
    navigator.clipboard.writeText(copyString.replaceAll("<br>", "\n"));
}
