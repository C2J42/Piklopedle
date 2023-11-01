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
            file.write("{\n\"creature\": [")
            for i in range(0, len(data)):
                e: Enemy = data[i]
                if (i < len(data)-1):
                    file.write(e.toJsonStr() + ",\n")
                else:
                    file.write(e.toJsonStr())
            file.write("\n]}")

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
        self.weight = -1 # default val
        self.health = -1 # default val
        self.appearances = [] # default val
        self.family = "" # default val
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
        return ("{" + 
                self.__toJsonStrHelper__("name", self.name) + "," +
                self.__toJsonStrHelper__("weight", self.weight) + "," +
                self.__toJsonStrHelper__("appearances", self.appearances) + "," +
                self.__toJsonStrHelper__("health", self.health) + ", " +
                self.__toJsonStrHelper__("family", self.family) + ", " +
                self.__toJsonStrHelper__("imgUrl", self.imgUrl)
                + "\n}")

    # helper func for toJsonStr
    def __toJsonStrHelper__(self, fieldName, fieldData):
        return "\n  \"" + fieldName + "\": \"" + str(fieldData) + "\""

    # Gets and parses URL data
    def getDataFromUrl(self):
        try:
            return requests.get(self.url).text
        except:
            print(self.url + "is not a valid url for enemy " + self.name + "!")
    
    # Helper method for parsing URL data
    def __parseUrlData__(self):
        #self.weight = self.__parseWeight__()
        self.appearances = self.__parseAppearances__()
        self.__parseTables__()
        self.family = self.__parseFamily__()
        self.imgUrl = self.__parseImageUrl__()
    

    # parse weight & health
    def __parseTables__(self):
        tableFlag = "carriers</a>"
        isScanning = False
        isReading = False
        startedNewRow = True
        tableData = [[]]
        rowNum = -1 # will get incremented before 1st use
        currStr = ""
        for i in range(0, len(self.urlText)):
            if isReading:
                if self.urlText[i] == "\n":
                    tableData[rowNum].append(currStr)
                    currStr = ""
                    isReading = False
                else: 
                    currStr = currStr + self.urlText[i]
            elif isScanning:
                if self.urlText[i-7: i+1] == "</table>": # prevent reading too much
                    break
                if self.urlText[i-3: i+1] == "<td>":
                    isReading = True
                elif self.urlText[i-3: i+1] == "<tr>":
                    tableData.append([])
                    rowNum += 1
            elif self.urlText[i-len(tableFlag)+1: i+1] == tableFlag:
                isScanning = True
        # get health from some weird thing:
        #   <span class="explain" title="For reference, in Pikmin 2, a Dwarf Red Bulborb has 200 HP,
        #    and a Red Bulborb has 750.">1100</span>
        try:
            for i in range(0, len(tableData)):
                try:
                    int(tableData[i][4]) # some already formatted correctly
                except:
                    tableData[i][4] = tableData[i][4].split(">")[1].split("<")[0]
        except IndexError:
            pass
        tableData.pop(len(tableData)-1)
        if (len(tableData)-1 == len(self.appearances)):
            tableData.pop(len(self.appearances)) # hey pikmin :/
        if self.name == "Bloomcap Bloyster": # so this on has 2 bits to carry
            self.weight = 8
        else:
            try:
                self.weight = int(tableData[len(tableData)-1][0])
            except: # for enemies w/o weight
                self.weight = 0
        try:
            self.health = int(tableData[len(tableData)-1][4])
        except:
            #print(self.name.upper())
            #print(tableData[len(tableData)-1][4])
            weirdos = [
                ["Ancient Sirehound", 9000*4], ["Waterwraith", 3300], ["Gatling Groink", 1200],
                ["Nectarous Dandelfly", 5], ["Unmarked Spectralids", 1]]
            for weirdo in weirdos:
                if self.name == weirdo[0]:
                    self.health = weirdo[1]
                    return True
            self.health = 0
        return True # if runs w/o errors


    # parse image URL
    def __parseImageUrl__(self):
        imageUrlFlag = "/File:"
        isReading = False
        imgUrl = ""
        for i in range(0, len(self.urlText)):
            if isReading:
                if self.urlText[i] == "\"":
                    break
                else:
                    imgUrl = imgUrl + self.urlText[i]
            elif self.urlText[i-len(imageUrlFlag)+1: i+1] == imageUrlFlag:
                isReading = True
        # surprisingly, this actually works for all enemies! No weirdos!

        # so this isn't the actual image url: its a link to a page with the image with the actual image url :/
        imgUrl = "https://pikmin.wiki/File:" + imgUrl
        try:
            urlText = requests.get(imgUrl).text
        except:
            print("Image url not working for enemy " + self.name + "!")
            print(imgUrl)
        actualImgUrlFlag = "fullMedia"
        isScanning = False
        isReading = False
        actualImgUrl = ""
        for i in range(0, len(urlText)):
            if isReading:
                if urlText[i] == "\"":
                    break
                else:
                    actualImgUrl = actualImgUrl + urlText[i]
            elif isScanning:
                if urlText[i-4: i+1] == "</p>": # prevent reading too much
                    break
                elif urlText[i-5: i+1] == "href=\"": # get stuff
                    isReading = True
            elif urlText[i-len(actualImgUrlFlag)+1: i+1] == actualImgUrlFlag:
                isScanning = True
        return actualImgUrl


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
        if (self.name == "Moss"): # for some reason Moss has special data?
            return [4]
        return rList
    

    def __parseFamily__(self):
        appearanceFlag = "<th>Family\n</th>"
        isScanning = False
        isReading = False
        rstr = ""
        for i in range(0, len(self.urlText)):
            if isReading:
                if self.urlText[i] == "\"" or self.urlText == ">":
                    break
                else:
                    rstr = rstr + self.urlText[i]
            elif isScanning:
                if self.urlText[i-4: i+1] == "</td>": # prevent reading too much
                    break
                elif self.urlText[i-6: i+1] == "title=\"": # get stuff
                    isReading = True
            elif self.urlText[i-len(appearanceFlag)+1: i+1] == appearanceFlag:
                isScanning = True
        if self.name == "Moss": # Moss, once again, is special
            rstr = "Space-dog family"
        elif rstr.strip() == "":
            rstr = "Unknown family"
        # truncate " family"
        return rstr[0:-7]


# returns a 2d list of enemies with same stats
def thingHelper(list):
    matches = []
    ignoreIndexes = []
    for i in range(0, len(list)):
        temp = [list[i].name]
        foundMatch = False
        if i not in ignoreIndexes:
            for j in range(i+1, len(list)):
                matching = True
                matching &= list[i].weight == list[j].weight
                matching &= list[i].health == list[j].health
                matching &= list[i].appearances[0] == list[j].appearances[0]
                if matching:
                    ignoreIndexes.append(j)
                    temp.append(list[j].name)
                    foundMatch = True
        if foundMatch:
            matches.append(temp)
    return matches


def main():
    ParseHandler.runParse()


main()
