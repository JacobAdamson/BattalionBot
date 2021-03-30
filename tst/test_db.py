from infrastructure.db import SqlLiteDom
import unittest
import os
import json
import sqlite3

class TestDomOperations(unittest.TestCase):
    
    defaultUsername = 'Creatif_Craxy'
    defaultBattalion = 'ugly'

    #TODO add alternate data 
    #TODO map all returns to entry

    def setUp(self):
        self.filename = "test_database.db"
        open(self.filename, "w").close()
        self.dom = SqlLiteDom(self.filename)

    def tearDown(self):
        os.remove(self.filename)

    def testCreateConnection(self):
        conn = self.dom.createConnection()
        self.assertTrue(conn.cursor())
        conn.close()

    def testKeyOperations(self):
        self.dom.createDatabaseTables()
        key = self.dom.getKey()
        self.assertEquals(None, key)
        key = self.dom.incremementKey()
        self.assertEquals(0, key)
        key = self.dom.getKey()
        self.assertEquals(0, key)
        index = self.dom.getIndex(key)
        self.assertTrue(index[0][1] > 10)

    def testRegisterChannel(self):
        self.dom.createDatabaseTables()
        self.dom.registerChannel(1616171771178818181818181881)
        self.dom.registerChannel(171717717)
        channels = self.dom.getChannels()
        self.assertEquals(2, len(channels))
        self.dom.clearChannels()
        channels = self.dom.getChannels()
        self.assertEquals(0, len(channels))

    def testEnlistUser(self):
        self.dom.createDatabaseTables()
        self.dom.enlistUser(self.defaultUsername)
        users = self.dom.getUsers()
        
        self.assertEquals(1, len(users))
        self.assertEquals(self.defaultUsername, users[0][0])

    def testDischargeUser(self):
        self.dom.createDatabaseTables()
        self.dom.enlistUser(self.defaultUsername)
        self.dom.dischargeUser(self.defaultUsername)
        users = self.dom.getUsers()
        self.assertEquals(0, len(users)) 

    def testGetJoinedStat(self):
        self.dom.createDatabaseTables()
        stat1a = {'data':{'segments':[{'stats':{'metric':{'value':2}}}]}}
        #stat1b = {'data':{'segments':[{'stats':{'metric':{'value':1}}}]}}
        stat2a = {'data':{'segments':[{'stats':{'metric':{'value':3}}}]}}
        stat2b = {'data':{'segments':[{'stats':{'metric':{'value':5}}}]}}
        stat3a = {'data':{'segments':[{'stats':{'metric':{'value':8}}}]}}
        stat3b = {'data':{'segments':[{'stats':{'metric':{'value':8}}}]}}
        self.dom.loadStat('usera',0, json.dumps(stat1a))
        #self.dom.loadStat('userb',0, json.dumps(stat1b))
        self.dom.loadStat('usera',1, json.dumps(stat2a))
        self.dom.loadStat('userb',1, json.dumps(stat2b))
        self.dom.loadStat('usera',2, json.dumps(stat3a))
        self.dom.loadStat('userb',2, json.dumps(stat3b))
        joinedStat = self.dom.getFriendlyJoinedStat(0, 1)
        self.assertEquals(2, len(joinedStat))

    def testGetFriendlyJoinedStat(self):
        self.dom.createDatabaseTables()
        stat1a = {'data':{'segments':[{'stats':{'metric':{'value':2}}}]}}
        stat2a = {'data':{'segments':[{'stats':{'metric':{'value':3}}}]}}
        stat2b = {'data':{'segments':[{'stats':{'metric':{'value':5}}}]}}
        stat3a = {'data':{'segments':[{'stats':{'metric':{'value':8}}}]}}
        stat3b = {'data':{'segments':[{'stats':{'metric':{'value':8}}}]}}
        self.dom.loadStat('usera',0, json.dumps(stat1a))
        self.dom.loadStat('usera',1, json.dumps(stat2a))
        self.dom.loadStat('userb',1, json.dumps(stat2b))
        self.dom.loadStat('usera',2, json.dumps(stat3a))
        self.dom.loadStat('userb',2, json.dumps(stat3b))
        joinedStat = self.dom.getFriendlyJoinedStat(0, 1)
        self.assertEquals(2, len(joinedStat))
        self.assertEquals(0, joinedStat[0][3])
        self.assertEquals(1, joinedStat[1][3])


    #### BANKING TESTS
    def testGetNoAccount(self):
        self.dom.createBankTables()
        account = self.dom.getAccount("user")
        self.assertEquals(len(account), 0)

    def testGetAccount(self):
        self.dom.createBankTables()
        self.dom.createAccount("user")
        account = self.dom.getAccount("user")
        self.assertEquals(len(account), 1)
        self.assertEquals(account[0][0], "user")
        self.assertEquals(account[0][1], 0)

    def testDeltaBalance(self):
        self.dom.createBankTables()
        self.dom.createAccount("user")
        self.dom.deltaBalance("user", 50)
        account = self.dom.getAccount("user")
        self.assertEqual(len(account), 1)
        self.assertEquals(account[0][0], "user")
        self.assertEquals(account[0][1], 50)
        self.dom.deltaBalance("user", -30)
        self.assertTrue(len(account), 1)
        account = self.dom.getAccount("user")
        self.assertEquals(account[0][1], 20)

    def testCreateDuplicateAccountFail(self):
        self.dom.createBankTables()
        self.dom.createAccount("user")
        self.assertRaises(
            sqlite3.IntegrityError,
             self.dom.createAccount,
              "user"
        )

    def createAndDropTable(self):
        self.dom.createBankTables()
        self.dom.createAccount("user")
        self.dom.dropBankTables()
        self.dom.createBankTables()
        account = self.dom.getAccount("user")
        self.assertEquals(len(account), 0)

    #### CONSCRIPTION TESTS #
    def testConscriptUser(self):
        self.dom.createGameAccountMappingTable()
        self.dom.conscriptUser("jacob", "psn", "creatif_craxy")
        account = self.dom.getAccountForPlatformUsername("psn", "creatif_craxy")
        self.assertEquals("jacob", account)

    def testConscriptUser(self):
        self.dom.createGameAccountMappingTable()
        self.dom.conscriptUser("jacob", "psn", "creatif_craxy")
        self.assertRaises(
            sqlite3.IntegrityError,
             self.dom.conscriptUser,
              "some_schmuck", "psn", "creatif_craxy"
        )

    def testGetAccountForPlatformUserName(self):
        self.dom.createGameAccountMappingTable()
        self.dom.conscriptUser("jacob", "psn", "creatif_craxy")
        accountMapping = self.dom.getAccountForPlatformUsername("psn", "creatif_craxy")
        self.assertEquals("jacob", accountMapping)

    def testGetAccountForPlatformUserName(self):
        self.dom.createGameAccountMappingTable()
        accountMapping = self.dom.getAccountForPlatformUsername("psn", "creatif_craxy")
        self.assertEquals(None, accountMapping)

    def testCreateAndDropTable(self):
        self.dom.createGameAccountMappingTable()
        self.dom.conscriptUser("jacob", "psn", "creatif_craxy")
        accountMapping = self.dom.getAccountForPlatformUsername("psn", "creatif_craxy")
        self.dom.dropMappingTable()
        self.dom.createGameAccountMappingTable()
        accountMapping = self.dom.getAccountForPlatformUsername("psn", "creatif_craxy")
        self.assertEquals(None, accountMapping)

    def testBattalionOperations(self):
        self.dom.createBattalionTables()
        self.dom.createBattalion("UGLY")
        battalions = self.dom.getBattalions()
        self.assertEquals(battalions[0][0], "UGLY")
        self.dom.setUserPermissionOnBattalion("jacob", "UGLY", "ADMIN")
        permissions = self.dom.getUserBattalionPermission("jacob", "COMMANDER")
        self.assertEquals(permissions[0][0], "COMMANDER")


if __name__ == '__main__':
    unittest.main()