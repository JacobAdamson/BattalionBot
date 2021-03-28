import analyzer
import loader
import unittest
import os
import json
from db import SqlLiteDom
import sqlite3 
import time
import datetime
from pytz import timezone

class TestTaskOperations(unittest.TestCase):
    def setUp(self):
        self.filename = "test_database.db"
        open(self.filename, "w").close()
        self.dom = SqlLiteDom(self.filename)
        self.dom.createDatabaseTables()
        self.dom.enlistUser('Creatif_Craxy')

    def tearDown(self):
        os.remove(self.filename)
    
    def testStoreAndIncrement(self):
        loader.storeAndIncrement(self.dom)
        loader.storeAndIncrement(self.dom)
        joinedStat = self.dom.getFriendlyJoinedStat(0, 1)
        self.assertEquals(1, len(joinedStat))
        self.assertEquals(4, len(joinedStat[0]))

    def testStoreData(self):
        loader.storeData(self.dom, 0)
        loader.storeData(self.dom, 1)
        joinedStat = self.dom.getFriendlyJoinedStat(0, 1)
        self.assertEquals(1, len(joinedStat))
        self.assertEquals(4, len(joinedStat[0]))

    def testDuplicateStores(self):
        loader.storeData(self.dom, 0)
        loader.storeData(self.dom, 1)
        self.assertRaises(sqlite3.IntegrityError, loader.storeData, self.dom, 1)

    def testGetTotalForPeriod(self):
        stat1a = {'data':{'segments':[{'stats':{'metric':{'value':2}}}]}}
        stat1b = {'data':{'segments':[{'stats':{'metric':{'value':1}}}]}}
        stat2a = {'data':{'segments':[{'stats':{'metric':{'value':3}}}]}}
        stat2b = {'data':{'segments':[{'stats':{'metric':{'value':5}}}]}}
        self.dom.loadStat('usera',0, json.dumps(stat1a))
        self.dom.loadStat('userb',0, json.dumps(stat1b))
        self.dom.loadStat('usera',1, json.dumps(stat2a))
        self.dom.loadStat('userb',1, json.dumps(stat2b))
        joinedStat = self.dom.getFriendlyJoinedStat(0, 1)
        periodTotal = analyzer.analyzeStatForPeriod(joinedStat, 'metric')
        
        self.assertEquals(5, periodTotal[2])
        self.assertEquals(4, periodTotal[1])
        self.assertEquals("userb", periodTotal[0])

    def testGetTotalForPeriodMissingData(self):
        stat1a = {'data':{'segments':[{'stats':{'metric':{'value':2}}}]}}
        stat2a = {'data':{'segments':[{'stats':{'metric':{'value':3}}}]}}
        stat2b = {'data':{'segments':[{'stats':{'metric':{'value':5}}}]}}
        self.dom.loadStat('usera',0, json.dumps(stat1a))
        self.dom.loadStat('usera',1, json.dumps(stat2a))
        self.dom.loadStat('userb',1, json.dumps(stat2b))
        joinedStat = self.dom.getFriendlyJoinedStat(0, 1)
        periodTotal = analyzer.analyzeStatForPeriod(joinedStat, 'metric')
        self.assertEquals(1, periodTotal[2])
        self.assertEquals(1, periodTotal[1])
        self.assertEquals("usera", periodTotal[0])

    def testGetTotalForPeriodNoData(self):
        joinedStat = self.dom.getFriendlyJoinedStat(0, 1)
        periodTotal = analyzer.analyzeStatForPeriod(joinedStat, 'metric')
        self.assertEquals(0, periodTotal[2])
        self.assertEquals(-1, periodTotal[1])
        self.assertEquals("nobody", periodTotal[0])

    def testCraftMessage(self):
        loader.storeAndIncrement(self.dom)
        loader.storeAndIncrement(self.dom)
        print(analyzer.craftMessage(self.dom, 0, 1))

    def testRealMessage(self):
        realDom = SqlLiteDom("actual_db_copy")
        report = analyzer.craftLastMessage(realDom)
        print(report)

    def testRealGetJoinedStat(self):
        realDom = SqlLiteDom("actual_db_copy")
        joinedStat = realDom.getJoinedStat(1, 2)
        creatifStatLine = None
        parizvalStatLine = None
        for statLine in joinedStat:
            if statLine[0] == "Creatif_Craxy":
                creatifStatLine = statLine
            elif statLine[0] == "ParzivalVii":
                parizvalStatLine = statLine
        self.assertTrue(creatifStatLine != None)
        self.assertTrue(parizvalStatLine != None)

        creatifKills = analyzer.getStatDiffFromLine(creatifStatLine, "kills", "overview")
        parizvalKills = analyzer.getStatDiffFromLine(parizvalStatLine, "kills", "overview")
        self.assertEquals(68, creatifKills)
        self.assertEquals(172, parizvalKills)
        sqlTemplate = "SELECT * FROM stats where username='%s' and key = %s"

        newStats = realDom.performQuery(sqlTemplate % ("Creatif_Craxy", 2))
        prevStats = realDom.performQuery(sqlTemplate % ("Creatif_Craxy", 1))
        newStatJson = json.loads(newStats[0][2])
        prevStatJson = json.loads(prevStats[0][2])
        newKills = newStatJson['data']['segments'][0]['stats']['kills']['value']
        prevKills = prevStatJson['data']['segments'][0]['stats']['kills']['value']
        prevPlatformId = prevStatJson['data']['platformInfo']['platformUserIdentifier']
        newPlatformId = newStatJson['data']['platformInfo']['platformUserIdentifier']
        prevLastUpdated = prevStatJson['data']['metadata']['lastUpdated']['value']
        newLastUpdated = newStatJson['data']['metadata']['lastUpdated']['value']
        self.assertEquals(creatifKills, newKills - prevKills)
        self.assertEquals(newPlatformId, 'creatif_craxy')
        self.assertEquals(prevPlatformId, newPlatformId)
    
    def trackUpdates(self):
        query = analyzer.queryBfTracker('Creatif_Craxy')
        intialKills = query['data']['segments'][0]['stats']['kills']['value']
        initialTime = query['data']['segments'][0]['stats']['timePlayed']['value']
        killTotal = intialKills
        timeTotal = initialTime
        for i in range(2000):
            query = analyzer.queryBfTracker('Creatif_Craxy')
            updatedKills = query['data']['segments'][0]['stats']['kills']['value']
            updatedTime = query['data']['segments'][0]['stats']['timePlayed']['value']
            killDiff = updatedKills - killTotal
            timeDiff = updatedTime - timeTotal            
            totalKillDiff =  updatedKills - intialKills
            curTime = curTime = time.time()
            formattedCurTime = timezone('US/Pacific').localize(datetime.datetime.fromtimestamp(curTime)).astimezone(timezone('US/Pacific')).strftime("%m/%d/%Y, %H:%M:%S")
            formattedTimeDiff = datetime.timedelta(seconds = timeDiff)
            formattedTotalTimePlayed = datetime.timedelta(seconds = timeTotal)
            lastGameMap = analyzer.queryLastGame()['data']['reports'][0]['mapKey']
            lastGameTimestamp = analyzer.queryLastGame()['data']['reports'][0]['timestamp']
            formattedLastGameTime = timezone('US/Pacific').localize(datetime.datetime.fromtimestamp(lastGameTimestamp)).astimezone(timezone('US/Pacific')).strftime("%m/%d/%Y, %H:%M:%S")
            printedStatement = """STATS FOR TIME: %s. KILL TOTAL: %s TIME TOTAL %s \nKIll DIFF: %s TIME DIFF: %s""" % (formattedCurTime, killTotal, formattedTotalTimePlayed, killDiff, formattedTimeDiff)            
            print(printedStatement)
            print("TOTAL KILL DIFF %s" % totalKillDiff)
            print('LAST GAME: %s PLAYED AT: %s\n' % (lastGameMap, formattedLastGameTime))
            killTotal = updatedKills
            timeTotal = updatedTime
            time.sleep(20)



if __name__ == '__main__':
    unittest.main()