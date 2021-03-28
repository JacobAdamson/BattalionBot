import os
import requests
import json

from typing import List
from analyzer_models import *
from db import SqlLiteDom
from texttable import Texttable
from loader import *
import datetime
from pytz import timezone


### MESSAGE OPERATIONS ###
def craftLastMessage(dom):
    key = dom.getKey()
    return craftMessage(dom, key - 1, key)


def craftMessageSince(dom, since):
    key = dom.getKey()
    return craftMessage(dom, key - since, key)


def craftMessage(dom, prevKey, curKey):
    ### TIME ANALYSIS ###
    if prevKey < 0:
        return "```NOT ENOUGH DATA TO REPORT```"
    prevTime = dom.getIndex(prevKey)[0][1]
    curTime = dom.getIndex(curKey)[0][1]

    prevDatetime = datetime.datetime.fromtimestamp(prevTime)
    curDatetime = datetime.datetime.fromtimestamp(curTime)
    prevTimeFormatted = timezone('UTC').localize(prevDatetime).astimezone(timezone('US/Pacific')).strftime(
        "%m/%d/%Y, %H:%M:%S")
    curTimeFormatted = timezone('UTC').localize(curDatetime).astimezone(timezone('US/Pacific')).strftime(
        "%m/%d/%Y, %H:%M:%S")

    intervalStatement = "FOR PERIOD: %s\nTO %s" % (prevTimeFormatted, curTimeFormatted)

    ### BATTALION ANALYSIS ###
    joinedStatLine = dom.getFriendlyJoinedStat(prevKey, curKey)
    killAnalysis = analyzeStatForPeriod(joinedStatLine, 'kills')
    damageAnalysis = analyzeStatForPeriod(joinedStatLine, 'damage')
    winAnalysis = analyzeStatForPeriod(joinedStatLine, 'wins')
    lossAnalysis = analyzeStatForPeriod(joinedStatLine, 'losses')
    timeAnalysis = analyzeStatForPeriod(joinedStatLine, 'timePlayed')
    deathsAnalysis = analyzeStatForPeriod(joinedStatLine, 'deaths')
    winPercentage = round(winAnalysis[2] / (winAnalysis[2] + lossAnalysis[2] + .00000001), 2)  # avoid divide by zero
    overallKd = round(killAnalysis[2] / (deathsAnalysis[2] + .00000001), 2)

    messageSegments = []
    messageSegments.append("BATTALION STATS: ")
    messageSegments.append(intervalStatement)
    messageSegments.append("Total Play Time: %s" % (datetime.timedelta(seconds=timeAnalysis[2])))
    messageSegments.append("Total Wins: %s" % (winAnalysis[2]))
    messageSegments.append("Win Percentage: %s" % winPercentage)
    messageSegments.append("Total Damage: %s" % (damageAnalysis[2]))
    messageSegments.append("Total Kills: %s" % (killAnalysis[2]))
    messageSegments.append("Overall kd: %s" % (overallKd))

    ### LEADERBOARDS ###
    messageSegments.append("\nLEADERBOARD - GENERAL")

    messageSegments.append(
        createLeaderboard(joinedStatLine, LeaderboardConfig.createFromString("kills wins", 100)))

    messageSegments.append("\nMOST ACTIVE")
    messageSegments.append(
        createLeaderboard(joinedStatLine, LeaderboardConfig.createFromString("timePlayed", 10)))

    messageSegments.append("\nPER MINUTE STATS")
    messageSegments.append(
        createLeaderboard(joinedStatLine, LeaderboardConfig.createFromString(
            "ground.score/ground.timePlayed ground.kills/ground.timePlayed", 10)))

    messageSegments.append("\nBY CLASS")
    messageSegments.append("GROUND")
    messageSegments.append(
        createLeaderboard(joinedStatLine, LeaderboardConfig.createFromString("ground.kills ground.score", 5)))

    messageSegments.append("\nTANKS")
    messageSegments.append(
        createLeaderboard(joinedStatLine, LeaderboardConfig.createFromString("tanker.kills tanker.score", 5)))

    messageSegments.append("\nAIR")
    messageSegments.append(
        createLeaderboard(joinedStatLine, LeaderboardConfig.createFromString("pilot.kills pilot.score", 5)))

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


def createLiveLeaderboard(dom, query: str, numRows):
    joinedStat = createLiveStat(dom)
    leaderboardConfig = LeaderboardConfig.createFromString(query, numRows)
    return createLeaderboard(joinedStat, leaderboardConfig)


def createLeaderboard(joinedStat, leaderboardConfig: LeaderboardConfig):
    headers = generateHeaders(leaderboardConfig.statDefinitions)
    data = generateTableData(joinedStat, leaderboardConfig.statDefinitions)
    sortedAndFilteredData = sortAndFilter(data, 1, leaderboardConfig.numRows, True)
    table = createTable(headers, sortedAndFilteredData)
    return table.draw()


### GENERATE TABLE HEADERS ###
def generateHeaders(statDefinitions: List[StatDefinition]):
    headers = ["name"]
    for statDef in statDefinitions:
        header: str = ""
        if statDef.denominatorStat is None:
            header = statDef.stat.statkey
        else:
            header = statDef.stat.statkey[0]
            if statDef.denominatorStat.statkey == "timePlayed":
                header = header + "pm"
            else:
                header = header + "/" + statDef.denominatorStat.statkey[0]
        headers.append(header)
    return headers


### GENERATE TABLE DATA ###
def generateTableData(joinedStat, statDefinitions: List[StatDefinition]):
    tableRows = []
    for line in joinedStat:
        rowVals = [line[0]]
        for statDef in statDefinitions:
            statTotal = getStatTotalForSegment(line, statDef.stat)
            denominatorStatTotal = 0
            if statDef.denominatorStat is not None:
                denominatorStatTotal = getStatTotalForSegment(line, statDef.denominatorStat)
            if denominatorStatTotal == 0:
                rowVal = statTotal
                if statDef.stat.statkey == "timePlayed":
                    rowVal = datetime.timedelta(seconds=rowVal)
            else:
                rowVal = statTotal / denominatorStatTotal
                if statDef.denominatorStat.statkey == "timePlayed":
                    rowVal = rowVal * 60
            rowVals.append(rowVal)
        tableRows.append(rowVals)
    return tableRows


def getStatTotalForSegment(line, stat: SingleStat):
    diffTotal = 0
    for segment in stat.segments:
        if len(line) > 2:
            diffTotal = diffTotal + getStatDiffFromLine(line, stat.statkey, segment)
        else:
            diffTotal = diffTotal + getStatFromLine(line, stat.statkey, segment)
    return diffTotal


### SORT AND FILTER LIST ###
def sortAndFilter(rows, sortIndex, numToGrab, filterZeros):
    if (filterZeros):
        filteredRows = list(filter(lambda x: (x[sortIndex] != 0), rows))
    else:
        filteredRows = rows
    sortedRows = sorted(filteredRows, key=lambda x: x[sortIndex], reverse=True)
    for row in rows:
        row[0] = row[0][0:8]
    if numToGrab >= 0:
        return sortedRows
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


def getStatDiffFromLine(statLine, statkey, segment):
    prevStat = json.loads(statLine[1])
    curStat = json.loads(statLine[2])
    if segment == "overview":
        actualPrevStat = prevStat['data']['segments'][0]['stats'][statkey]['value']
        actualCurStat = curStat['data']['segments'][0]['stats'][statkey]['value']
    else:
        actualPrevStat = getValByClass(prevStat, statkey, segment)
        actualCurStat = getValByClass(curStat, statkey, segment)
    return actualCurStat - actualPrevStat


def getStatFromLine(statLine, statkey, segment):
    stat = json.loads(statLine[1])
    if segment == "overview":
        actualStat = stat['data']['segments'][0]['stats'][statkey]['value']
    else:
        actualStat = getValByClass(stat, statkey, segment)
    return actualStat


def getValByClass(jsonElement, statkey, classKey):
    segments = jsonElement['data']['segments']
    for segment in segments:
        if segment['type'] == "class":
            if segment['attributes']['class'] == classKey:
                return segment['stats'][statkey]['value']
