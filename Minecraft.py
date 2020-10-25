import os
import time
import _thread
import Discord
import json
import psutil

import config

__playersListInfo = {"lastUpdate": 0,"count": 0, "max": 0, "list": []}
__serverInfo = {"lastUpdate": 0, "tps1m": -1, "tps5m": -1, "tps15m": -1, "cpuUse": -1, "memUse": -1, "memTot": -1, "diskUse": -1, "diskTot": -1, "MapSize": -1}

def __minecraftLogParser():

    lastModifOnLogs = 0
    lastLogLine = ""

    while True :

        logFilePath = os.path.abspath(config.servDir)+"/logs/latest.log"

        if os.path.isfile(logFilePath) :

            stat = os.stat(logFilePath) # check si le fichier à été modifier.

            if lastModifOnLogs != stat.st_mtime :
                lastModifOnLogs = stat.st_mtime

                logFile = open(logFilePath, "r")
                logLines = logFile.readlines()
                logFile.close()

                newLogLines = []

                if lastLogLine != "":
                    if lastLogLine in logLines :
                        lastLineIndex = logLines.index(lastLogLine)
                        newLogLines = logLines[lastLineIndex+1:]
                    else :
                        newLogLines = logLines
                if len(logLines) > 0 :
                    lastLogLine = logLines[-1]


                for line in newLogLines :

                    line = line.replace("\n", "")

                    if "Async Chat Thread" in line :
                        __minecraftChatParser(line)
                    elif "Server thread/INFO" in line :
                        __minecraftServerInfoParser(line)


        else :
            print("[ERROR] '"+logFilePath+"' do not exist.")

        time.sleep(0.5)

def __minecraftChatParser(rawMsg):

    pseudo = ""
    msg = ""

    if len(rawMsg) > 11 :
        rawMsg = rawMsg[11:]

        headerEndIndex = rawMsg.index(":")
        rawMsg = rawMsg[headerEndIndex+1:]

        pseudoStartIndex = rawMsg.index("<") + 1
        pseudoEndIndex = rawMsg.index(">")

        msgStartIndex = pseudoEndIndex + 2

        pseudo = rawMsg[pseudoStartIndex : pseudoEndIndex]
        msg = rawMsg[msgStartIndex : ]

        Discord.sendPlayerMsg(pseudo, msg)

def __minecraftServerInfoParser(rawMsg):
    if "Server thread/INFO" in rawMsg :
        startIndex = rawMsg.index("INFO") + 7
        rawMsg = rawMsg[startIndex:]

        if "players online" in rawMsg :
            __minecraftListParser(rawMsg)
        elif "joined the game" in rawMsg:
            __minecraftConnectParser(rawMsg)
        elif "left the game" in rawMsg:
            __minecraftConnectParser(rawMsg)
        elif "TPS from last" in rawMsg:
            __minecraftTpsParser(rawMsg)

def __minecraftListParser(rawMsg):
    splitText = rawMsg.split(":")
    print("[DEBUG] list Parser")
    if len(splitText) >= 2 and len(splitText[0].split(" ")) >= 8 :
        playersCount = int(splitText[0].split(" ")[2])
        playersMax = int(splitText[0].split(" ")[7])
    else :
        playersCount = 0
        playersMax = 0

    if len(splitText) >= 2 :
        playersList = splitText[1].split(",")
        newPlayersList = []
        for player in playersList :
            newPlayersList += [player.split(" ")[-1]]
        playersList = newPlayersList
    else :
        playersList = []


    __playersListInfo["lastUpdate"] = time.time()
    __playersListInfo["count"] = playersCount
    __playersListInfo["max"] = playersMax
    __playersListInfo["list"] = playersList

def __minecraftConnectParser(rawMsg):
    splitMsg = rawMsg.split(" ")

    pseudo = splitMsg[-4]
    type = splitMsg[-3]

    msg = ""
    if type == "left":
        msg += "**" + pseudo + "** a quitté le jeu"
        print("[INFO] "+msg)
        Discord.sendBotMsg(msg)
    elif type == "joined":
        msg += "**" + pseudo + "** a rejoint le jeu"
        print("[INFO] "+msg)
        Discord.sendBotMsg(msg)

def __minecraftTpsParser(rawMsg):
    print("[INFO] parse TPS ", rawMsg)

    msgSplit = rawMsg.split(" ")

    __serverInfo["tps1m"]  = float(msgSplit[6].replace(",", ""))
    __serverInfo["tps5m"]  = float(msgSplit[7].replace(",", ""))
    __serverInfo["tps15m"] = float(msgSplit[8].replace(",", ""))

    __serverInfo["lastUpdate"] = time.time()

    print(__serverInfo)

def loadPlayersDBJson():

    if os.path.isfile('playersDB.json'):
        playersDBFile = open('playersDB.json', 'r')
        playersDB = json.loads(playersDBFile.read())
        playersDBFile.close()
    else :
        playersDB = []

    whitelistFile = open(os.path.abspath(config.servDir)+"/whitelist.json", 'r')
    whitelist = json.loads(whitelistFile.read())
    whitelistFile.close()

    for player in whitelist :

        isInDB = False

        for DBitem in playersDB :
            if DBitem['minecraft-pseudo'] == player['name'] :
                DBitem['minecraft-uuid'] = player['uuid']
                isInDB = True



        if not isInDB :
            newDBItem = {
                'minecraft-pseudo': player['name'],
                'minecraft-uuid': player['uuid'],
                'minecraft-head-url': "",
                'discord-pseudo': ""
            }
            playersDB += [newDBItem]

    playersDBFile = open('playersDB.json', 'w')
    playersDBFile.write(json.dumps(playersDB, sort_keys=True, indent=4))
    playersDBFile.close()


def startLogParser():
    _thread.start_new_thread(__minecraftLogParser, ())
    loadPlayersDBJson()

def serverIsAlive():

    servInputFilePath = os.path.abspath(config.servDir)+"/serv-input"

    __serverInfo["cpuUse"]  = psutil.cpu_percent()

    memStat = psutil.virtual_memory()
    __serverInfo["memUse"]  = memStat.used
    __serverInfo["memTot"]  = memStat.total

    diskStat = psutil.disk_usage(os.path.abspath(config.servDir))
    __serverInfo["diskUse"]  = diskStat.used
    __serverInfo["diskTot"]  = diskStat.total

    if os.path.isfile(servInputFilePath) :
        print("[INFO] serv file ok.")

        now = time.time()
        executeCmd("tps")

        timeout = 100
        while __serverInfo["lastUpdate"] <= now:
            time.sleep(0.1)
            timeout -= 1
            if timeout <= 0 :
                print("[INFO] TPS info timeout")
                return False

        return True

    else :
        return False

def serverStat():

    out = {"alive": False, "tps1m": -1, "tps5m": -1, "tps15m": -1, "cpuUse": -1, "memUse": -1, "memTot": -1, "diskUse": -1, "diskTot": -1, "MapSize": -1}

    if serverIsAlive():
        out["alive"]  = True
        out["tps1m"]  = __serverInfo["tps1m"]
        out["tps5m"]  = __serverInfo["tps5m"]
        out["tps15m"] = __serverInfo["tps15m"]
    else :
        out["alive"] = False

    out["cpuUse"]  = __serverInfo["cpuUse"]
    out["memUse"]  = __serverInfo["memUse"]
    out["memTot"]  = __serverInfo["memTot"]
    out["diskUse"] = __serverInfo["diskUse"]
    out["diskTot"] = __serverInfo["diskTot"]
    out["MapSize"] = __serverInfo["MapSize"]

    return out


def getPlayersList(maj=True):
    playerInfo = {"count": 0, "max": 0, "list": []}

    if maj :
        now = time.time()
        executeCmd("list")

        timeout = 100
        while __playersListInfo["lastUpdate"] <= now:
            time.sleep(0.1)
            timeout -= 1
            if timeout <= 0 :
                print("[ERROR] list info timeout")
                break

    playerInfo["count"] = __playersListInfo["count"]
    playerInfo["max"] = __playersListInfo["max"]
    playerInfo["list"] = __playersListInfo["list"]

    return playerInfo

def sayOnChat(pseudo, msg):

    print("[INFO] say on minecraft : [Discord]<"+pseudo+"> "+msg)

    msg = msg.replace("\\", "\\\\")
    msg = msg.replace("\"", "\\\"")


    tellRawArg  = "[\"\","
    tellRawArg += "{\"text\":\"[\"},"
    tellRawArg += "{\"text\":\"Discord\", \"color\":\"dark_aqua\"},"
    tellRawArg += "{\"text\":\"]<"+pseudo+"> "+msg+"\"}]"


    bashCMD = "screen -S minecraft -X stuff \"tellraw @a "+tellRawArg+"\\n\""
    executeCmd("tellraw @a "+tellRawArg)

def executeCmd(cmd):
    print("[INFO] execute minecraft command : "+cmd)

    bashCMD = "screen -S minecraft -X stuff \""+cmd+"\n\""

    minecraftConsole = open(os.path.abspath(config.servDir)+"/serv-input", "w")
    minecraftConsole.write(cmd+"\n")
