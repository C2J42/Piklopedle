import requests

class ParseHandler:
    # all needed data has <li>
    # start/end at certain lines to avoid some bad data (hey pikmin enemies)
    #   starting line not needed! flag text for end: "Icon for the Yellow Wollyhop, from Pikmin 4"
    @staticmethod
    def __initialParse__():
        readFile = open("pikipediaEnemyPage.html", "r")
        writeFile = open("enemyParsing.txt", "w")
        lineOut = "default"
        while (lineOut != ""): # "" if end of file
            try:
                lineOut = readFile.readline()
                if ("<li>" in lineOut):
                    writeFile.write(lineOut)
                    # ending before it gets to hey pikmin
                    if ("Icon for the Yellow Wollyhop, from Pikmin 4" in lineOut):
                        lineOut = ""
            except UnicodeDecodeError:
                pass
        readFile.close()
        writeFile.close()

    # change strange html into: "<Enemy>: <wiki link>"
    @staticmethod
    def __filterExcess__():
        lineList = []
        with open("enemyParsing.txt", "r") as file:
            lineList = file.readlines()
        for i in range(0, len(lineList)):
            lineList[i] = ParseHandler.__lineParse__(lineList[i])
        with open("enemyParsing.txt", "w") as file:
            file.writelines(lineList)

    # helper for refineParse()
    @staticmethod
    def __lineParse__(str):
        # begin after <a href=" (9) and title=" (7)
        haveUrl = False
        urlStr = ""
        nameStr = ""

        lastSeven = ""
        isScanning = False
        for i in range(7, len(str)): # begin at 7 to avoid index exceptions
            # if isScanning, take data inputs
            if isScanning:
                if str[i] == "\"":
                    isScanning = False
                    if not haveUrl:
                        haveUrl = True
                    else: # just finished getting name
                        break
                else:
                    if not haveUrl:
                        urlStr = urlStr + str[i]
                    else: # has url, not name
                        nameStr = nameStr + str[i]
            # else, search for begin flags
            else:
                if str[i] == "\"":
                    if str[i-7:i] == " title=" or str[i-7:i] == "a href=":
                        isScanning = True
        return nameStr + ", " + urlStr + "\n"

    # sorts the parsed data
    @staticmethod
    def __sortParsedData__():
        intialList = []
        sortList = []
        with open("enemyParsing.txt", "r") as file:
            initialList = file.readlines()
        for elem in initialList:
            # account for name changes: they link to same page anyway
            if "Yellow Wollywog" in elem:
                elem = "Yellow Wollyhop, https://www.pikminwiki.com/Yellow_Wollyhop\n"
            elif "Wollywog" in elem:
                elem = "Wollyhop, https://www.pikminwiki.com/Wollyhop\n"
            elif "Wogpole" in elem:
                elem = "Wolpole, https://www.pikminwiki.com/Wolpole\n"
            if elem not in sortList:
                sortList.insert(ParseHandler.__sortedInsertIndex__(sortList, elem), elem)
        with open("enemyParsing.txt", "w") as file:
            file.writelines(sortList)

    # returns index to put if maintaining ascending sort order
    @staticmethod
    def __sortedInsertIndex__(list, elem):
        if (len(list) == 0):
            return 0
        elif (len(list) == 1):
            if elem < list[0]:
                return 0
            else:
                return 1
        else:
            for i in range(0, len(list)):
                if elem < list[i]:
                    return i
            return len(list)

    # reads data from the file, 
    @staticmethod
    def getData():
        data = []
        with open("enemyParsing.txt", "r") as file:
            lineStr = "default"
            while (lineStr != ""):
                lineStr = file.readline()
                lineData = lineStr.strip().split(", ")
                try:
                    data.append(Enemy(lineData[0], lineData[1]))
                    print(data[len(data)-1]) # for funsies and to tell its running
                except:
                    pass
        return data

    # writes to the creatureData.json file
    @staticmethod
    def __writeToJson__():
        data = ParseHandler.getData()
        with open("creatureData.json", "w") as file:
            file.write("{\n")
            for i in range(0, len(data)):
                e: Enemy = data[i]
                if (i < len(data)-1):
                    file.write(e.toJsonStr() + ",\n")
                else:
                    file.write(e.toJsonStr())
            file.write("\n}")

    # runs the parse
    @staticmethod
    def runParse():
        # get data
        ParseHandler.__initialParse__()
        # refine data
        ParseHandler.__filterExcess__()
        # sort & remove dupes
        ParseHandler.__sortParsedData__()
        # get data from subsites
        ParseHandler.__writeToJson__()


class Enemy:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.urlText = self.getDataFromUrl()
        self.__parseUrlData__()
    
    # to string, returns name
    def __str__(self):
        return self.name

    # equal if Enemies have same name
    def __eq__(self, other):
        return self.name == other.name

    # turns enemy data in json-formatted string
    def toJsonStr(self):
        return ("\"" + self.name + "\": {" + 
                self.__toJsonStrHelper__("weight", self.weight) + "," +
                self.__toJsonStrHelper__("appearances", self.appearances)
                + "\n}")

    # helper func for toJsonStr
    def __toJsonStrHelper__(self, fieldName, fieldData):
        if (isinstance(fieldData, str)):
            fieldData = "\"" + fieldData + "\""
        return "\n  \"" + fieldName + "\": " + str(fieldData)

    # Gets and parses URL data
    def getDataFromUrl(self):
        try:
            return requests.get(self.url).text
        except:
            print(self.url + "is not a valid url for enemy " + self.name + "!")
    
    # Helper method for parsing URL data
    def __parseUrlData__(self):
        self.weight = self.__parseWeight__()
        self.appearances = self.__parseAppearances__()
    
    # gets enemy weight
    def __parseWeight__(self):
        weightFlag = "carriers</a>"
        isScanning = False
        isReading = False
        startedNewRow = True
        weights = []
        weightStr = ""
        for i in range(0, len(self.urlText)):
            if isReading:
                if self.urlText[i] == "\n":
                    try:
                        #int(weightStr)
                        weights.append(int(weightStr))
                        isScanning = False
                    except:
                        isScanning = True
                        weightStr = ""
                        isReading = False
                        startedNewRow = False
                    #if not isScanning: break
                else: 
                    weightStr = weightStr + self.urlText[i]
            elif isScanning:
                if self.urlText[i-7: i+1] == "</table>": # prevent reading too much
                        break
                if startedNewRow:
                    if self.urlText[i-3: i+1] == "<td>":
                        isReading = True
                else:
                    if self.urlText[i-3: i+1] == "<tr>":
                        startedNewRow = True
            elif self.urlText[i-len(weightFlag)+1: i+1] == weightFlag:
                isScanning = True
        try:
            return weights[len(weights)-1]
        except:
            # one cause for error: enemies that didn't have weight in 1, but had weight in others - FIXED
            #   other cause: some enemies simply have no weight! - Should be caught!
            # print("Error for " + self.name + "!")

            # so this now only runs for enemies w/o weight. it prevents program termination and returns 0

            return 0

    # gets list of games enemy appeared in
    def __parseAppearances__(self):
        appearanceFlag = "<th style=\"width: 30%;\">Appears in"
        isScanning = False
        isReading = False
        gamesList = ["Pikmin", "Pikmin 2", "Pikmin 3", "Pikmin 4"]
        rList = []
        tempStr = ""
        for i in range(0, len(self.urlText)):
            if isReading:
                if self.urlText[i] == "<":
                    # turn tempstr data into an appearance
                    for i in range(0, 4):
                        if (tempStr == gamesList[i]):
                            rList.append(i+1)
                    tempStr = ""
                    isReading = False
                else:
                    tempStr = tempStr + self.urlText[i]
            elif isScanning:
                if self.urlText[i-4: i+1] == "</td>": # prevent reading too much
                    break
                elif self.urlText[i-2: i+1] == "<i>": # get stuff in between <i> and <\i>
                    isReading = True
            elif self.urlText[i-len(appearanceFlag)+1: i+1] == appearanceFlag:
                isScanning = True
        return rList


def main():
    ParseHandler.runParse()

main()
