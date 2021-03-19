import os
import requests
import json
from db import SqlLiteDom
from texttable import Texttable
import datetime
from pytz import timezone
### DATA STORE OPERATIONS ###
def storeAndIncrement(dom):
    key = dom.incremementKey()
    storeData(dom, key)
    return key

def storeData(dom, key):
    users = dom.getUsers()
    for user in users:
        data = queryBfTracker(user[0])
        stringifyedData = json.dumps(data)
        dom.loadStat(user[0], key, stringifyedData)

### MESSAGE OPERATIONS ###
def craftLastMessage(dom):
    key = dom.getKey()
    return craftMessage(dom, key - 1, key)

def craftMessageSince(dom, since):
    key = dom.getKey()
    return craftMessage(dom, key - since, key)

def craftMessage(dom, prevKey, curKey):
    ### TIME ANALYSIS ###
    if(prevKey < 0):
        return "```NOT ENOUGH DATA TO REPORT```"
    prevTime = dom.getIndex(prevKey)[0][1]
    curTime = dom.getIndex(curKey)[0][1]

    
    prevDatetime = datetime.datetime.fromtimestamp(prevTime)
    curDatetime = datetime.datetime.fromtimestamp(curTime)
    prevTimeFormatted = timezone('UTC').localize(prevDatetime).astimezone(timezone('US/Pacific')).strftime("%m/%d/%Y, %H:%M:%S")
    curTimeFormatted = timezone('UTC').localize(curDatetime).astimezone(timezone('US/Pacific')).strftime("%m/%d/%Y, %H:%M:%S")

    intervalStatement = "FOR PERIOD: %s\nTO %s" % (prevTimeFormatted, curTimeFormatted)


    ### BATTALION ANALYSIS ###
    joinedStatLine = dom.getFriendlyJoinedStat(prevKey, curKey)
    killAnalysis = analyzeStatForPeriod(joinedStatLine , 'kills')
    damageAnalysis = analyzeStatForPeriod(joinedStatLine , 'damage')
    winAnalysis = analyzeStatForPeriod(joinedStatLine , 'wins')
    lossAnalysis = analyzeStatForPeriod(joinedStatLine , 'losses')
    timeAnalysis = analyzeStatForPeriod(joinedStatLine, 'timePlayed')
    deathsAnalysis = analyzeStatForPeriod(joinedStatLine, 'deaths')
    winPercentage = round(winAnalysis[2]/(winAnalysis[2] + lossAnalysis[2] + .00000001), 2) #avoid divide by zero
    overallKd = round(killAnalysis[2]/(deathsAnalysis[2] + .00000001), 2)
    
    messageSegments = []
    messageSegments.append("BATTALION STATS: ")
    messageSegments.append(intervalStatement)
    messageSegments.append("Total Play Time: %s" % (datetime.timedelta(seconds = timeAnalysis[2])))
    messageSegments.append("Total Wins: %s" % (winAnalysis[2]))
    messageSegments.append("Win Percentage: %s" % winPercentage)
    messageSegments.append("Total Damage: %s" % (damageAnalysis[2]))
    messageSegments.append("Total Kills: %s" % (killAnalysis[2]))
    messageSegments.append("Overall kd: %s" % (overallKd))

    ### LEADERBOARDS ###
    messageSegments.append("\nLEADERBOARD - GENERAL")
    messageSegments.append(createLeaderboard(joinedStatLine, ["kills", "wins"], ["overview"], 100, True))
    
    messageSegments.append("\nMOST ACTIVE")
    messageSegments.append(createTimeBoard(joinedStatLine, 10))

    messageSegments.append("\nTOP 5's")
    messageSegments.append("GROUND")
    messageSegments.append(createLeaderboard(joinedStatLine, ["kills", "score"], ["assault", "medic", "support", "recon"], 5, True))

    messageSegments.append("\nTANKS")
    messageSegments.append(createLeaderboard(joinedStatLine, ["kills", "score"], ["tanker"], 5, False))

    messageSegments.append("\nAIR")
    messageSegments.append(createLeaderboard(joinedStatLine, ["kills", "score"], ["pilot"], 5, False))
    
    report = "\n".join(messageSegments)
    return "```" + report + "```" 

def analyzeStatForPeriod(joinedStat, statkey):
    sum = 0
    curMax = -1
    username = "nobody"
    for i in range(len(joinedStat)):
        statLine = joinedStat[i]
        diff = getStatDiffFromLine(statLine, statkey, "overview")
        sum = sum + diff
        if (diff > curMax):
            curMax = diff
            username = statLine[0]
    return (username, curMax, sum)

def createLeaderboard(joinedStat, keysToGrab, segments, rowsToGrab, getKd):
    headers = generateHeaders(keysToGrab, getKd)
    data = generateTableData(joinedStat, keysToGrab, segments, rowsToGrab, getKd)
    sortedAndFilteredData = sortAndFilter(data, 1, rowsToGrab, True)
    table = createTable(headers, sortedAndFilteredData)
    return table.draw()
      

### GENERATE TABLE HEADERS ###
def generateHeaders(keysToGrab, getKd):
    headers = ["name"]
    for key in keysToGrab:
        headers.append(key)
    if getKd:
        headers.append("kd")
    return headers

### GENERATE TABLE DATA ###
def generateTableData(joinedStat, keysToGrab, segments, rowsToGrab, getKd):
    array = []
    for line in joinedStat:
        rowVals = [line[0][0:8]]
        for key in keysToGrab:
            diffTotal = 0
            for segment in segments:
                diffTotal = diffTotal + getStatDiffFromLine(line, key, segment)
            rowVals.append(diffTotal)
        if getKd:
            totalKills = 0
            totalDeaths = 0
            for segment in segments:
                totalKills = totalKills + getStatDiffFromLine(line, 'kills', segment)
                totalDeaths = totalDeaths + getStatDiffFromLine(line, 'deaths', segment)
            rowVals.append(totalKills/(totalDeaths + .00000001))
        array.append(rowVals)
    return array

### SORT AND FILTER LIST ###
def sortAndFilter(rows, sortIndex, numToGrab, filterZeros):
    if(filterZeros):
        filteredRows = list(filter(lambda x: (x[sortIndex] != 0) , rows))
    else:
        filteredRows = rows
    sortedRows = sorted(filteredRows, key = lambda x: x[sortIndex], reverse = True)
    if(numToGrab >= 0):
        return sortedRows[0:numToGrab]
    else:
        return sortedRows

### CREATE ACTUAL TABLE ###
def createTable(headers, rows):
    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.set_precision(2)
    table.set_max_width(32)
    table.header(headers)
    for row in rows:
        table.add_row(row)
    return table


#def createShoutouts(joinedStat):
#    shoutoutSegments = []
#    revivesStat = analyzeStatForPeriod(joinedStat, 'revives')
#    shoutoutSegments.append("Good Samaritan:\n%s - %s revives" % (revivesStat[0], revivesStat[1])

def createTimeBoard(joinedStat, rowsToGrab):
    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.header(["name", "time played"])
    table.set_max_width(30)

    i = rowsToGrab
    array = []
    for line in joinedStat:
        username = line[0][0:8]
        timePlayed = getStatDiffFromLine(line,'timePlayed', "overview")
        array.append((username, timePlayed))

    sortedList = sorted(array, key = lambda x: x[1], reverse = True)
    for line in sortedList:
        if(rowsToGrab < 1):
            break
        formattedTimePlayed = datetime.timedelta(seconds = line[1])
        if(line[1] != 0):
            table.add_row([line[0], formattedTimePlayed])
        rowsToGrab = rowsToGrab - 1
    return table.draw()

def getStatDiffFromLine(statLine, statkey, segment):
    prevStat = json.loads(statLine[1])
    curStat = json.loads(statLine[2])
    if(segment == "overview"):
        actualPrevStat = prevStat['data']['segments'][0]['stats'][statkey]['value']
        actualCurStat = curStat['data']['segments'][0]['stats'][statkey]['value']
    else: 
        actualPrevStat = getValByClass(prevStat, statkey, segment)
        actualCurStat = getValByClass(curStat, statkey, segment)
    return actualCurStat - actualPrevStat

def getValByClass(jsonElement, statkey, classKey):
    segments = jsonElement['data']['segments']
    for segment in segments:
        if segment['type'] == "class":
            if segment['attributes']['class'] == classKey:
                return segment['stats'][statkey]['value']
    

def queryBfTracker(username): 
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36'}
    return requests.get('https://api.tracker.gg/api/v2/bfv/standard/profile/psn/' + username + '?forceCollect=true', headers=headers).json()

def queryLastGame(username):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36'}
    return requests.get('https://api.tracker.gg/api/v1/bfv/gamereports/psn/latest/' + username, headers=headers).json()