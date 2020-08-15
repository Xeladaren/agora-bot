import os
import time
import _thread
import Discord

import config

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

                lastLogLine = logLines[-1]


                for line in newLogLines :

                    line = line.replace("\n", "")

                    if "Async Chat Thread" in line :
                        __minecraftChatParser(line)


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

        Discord.senPlayerMsg(pseudo, msg)

def startLogParser():
    _thread.start_new_thread(__minecraftLogParser, ())

def sayOnChat(pseudo, msg):
    print("say on chat")

def executeCmd(cmd):
    print("minecraft cmd")
