import unittest
import hr
import os
import json
from db import SqlLiteDom

class TestHr(unittest.TestCase):
    def setUp(self):
        self.filename = "test_database.db"
        open(self.filename, "w").close()
        self.dom = SqlLiteDom(self.filename)
        self.dom.createDatabaseTables()
        self.dom.createBankTables()
        self.dom.createGameAccountMappingTable()

    def tearDown(self):
        os.remove(self.filename)

    def testProcessPerformace(self):
        hr.conscript(self.dom, "jacob", "psn", "creatif_craxy")
        stat0a = {'data':{'segments':[{'stats':{'wins':{'value':1},"kills":{'value':0}}}]}}
        stat0b = {'data':{'segments':[{'stats':{'wins':{'value':5},"kills":{'value':100}}}]}}
        self.dom.loadStat('creatif_craxy',0, json.dumps(stat0a))
        self.dom.loadStat('creatif_craxy',1, json.dumps(stat0b))
        hr.processPerformance(self.dom, 0, 1)
        self.assertEquals(self.dom.balance("jacob"), 5)

    def testReport(self):
        hr.conscript(self.dom, "jacob", "psn", "creatif_craxy")
        stat0a = {'data':{'segments':[{'stats':{'wins':{'value':1},"kills":{'value':0}}}]}}
        stat0b = {'data':{'segments':[{'stats':{'wins':{'value':5},"kills":{'value':100}}}]}}
        self.dom.loadStat('creatif_craxy',0, json.dumps(stat0a))
        self.dom.loadStat('creatif_craxy',1, json.dumps(stat0b))
        performanceInfo = hr.processPerformance(self.dom, 0, 1)
        self.assertEquals(self.dom.balance("jacob"), 5)
        report = hr.generateReports(performanceInfo, None)
        print(report)


    def testComplexPerformace(self):
        hr.conscript(self.dom, "jacob", "psn", "creatif_craxy")
        hr.conscript(self.dom, "noah", "psn", "ugly_noah")
        stat0a = {'data':{'segments':[{'stats':{'wins':{'value':1},"kills":{'value':0}}}]}}
        stat0b = {'data':{'segments':[{'stats':{'wins':{'value':5},"kills":{'value':100}}}]}}
        self.dom.loadStat('creatif_craxy',0, json.dumps(stat0a))
        self.dom.loadStat('creatif_craxy',1, json.dumps(stat0b))
        self.dom.loadStat('ugly_noah',0, json.dumps(stat0a))
        self.dom.loadStat('ugly_noah',1, json.dumps(stat0b))
        hr.processPerformance(self.dom, 0, 1)
        self.assertEquals(self.dom.balance("jacob"), 5)
        self.assertEquals(self.dom.balance("noah"), 5)

    
    def testAwardTokensToGameAccounts(self):
        hr.conscript(self.dom, "jacob", "psn", "creatif_craxy")
        hr.conscript(self.dom, "jacob", "psn", "my_alt")
        hr.conscript(self.dom, "noah", "psn", "uglynoah")
        table = [["creatif_craxy", 10], ["my_alt", 3], ["uglynoah", 8]]
        hr.awardTokensToGameAccounts(self.dom, table)
        self.assertEquals(self.dom.balance("jacob"), 13)
        self.assertEquals(self.dom.balance("noah"), 8)

    def testAwardTokensToGameAccounts(self):
        hr.conscript(self.dom, "jacob", "psn", "creatif_craxy")
        hr.conscript(self.dom, "jacob", "psn", "my_alt")
        hr.conscript(self.dom, "noah", "psn", "uglynoah")
        table = [["creatif_craxy", 10, 0], ["my_alt", 3, 0], ["uglynoah", 8, 0]]
        hr.awardTokensToGameAccounts(self.dom, table)
        self.assertEquals(self.dom.balance("jacob"), 13)
        self.assertEquals(self.dom.balance("noah"), 8)
        

    def testConscript(self):
        hr.conscript(self.dom, "jacob", "psn", "creatif_craxy")
        print(self.dom.getUsers())
        self.assertTrue(self.dom.userExists("creatif_craxy"))
        self.assertTrue(self.dom.hasAccount("jacob"))
        account = self.dom.getAccountForPlatformUsername("psn", "creatif_craxy")
        self.assertEquals(account, "jacob")

if __name__ == '__main__':
    unittest.main()