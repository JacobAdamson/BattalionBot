import sqlite3
from sqlite3 import Error
import time

class SqlLiteDom:
    def __init__(self, filename):
        self.filename = filename

    #### USER OPERATIONS ####
    def getUsers(self):
        sql = "SELECT * FROM USERS"
        return self.performQuery(sql)

    def enlistUser(self, psnUser):
        #validate battalion exists
        sql = """INSERT INTO USERS (username)
        VALUES ('%s')""" % (psnUser)
        return self.performWrite(sql)

    def dischargeUser(self, psnUser):
        #check user status
        sql = """ DELETE FROM USERS
        WHERE username = '%s'""" % (psnUser)
        return self.performWrite(sql)

    def userExists(self, username):
        sql = f"SELECT * from users where username = '{username}'"
        usersWithUsername = self.performQuery(sql)
        return len(usersWithUsername) == 1

    #### MAPPING OPERATIONS ####
    def conscriptUser(self, username, platform, platformUsername):
        sql = f"""INSERT INTO gameAccountMapping (username, platform, platformUsername) values ('{username}','{platform}','{platformUsername}')"""
        return self.performWrite(sql)

    def getAccountForPlatformUsername(self, platform, platformUsername):
        sql = f"""SELECT username from gameAccountMapping where platform='{platform}' and platformUsername='{platformUsername}'"""
        mapping = self.performQuery(sql)
        if(len(mapping) != 1):
            return None
        else:
            return mapping[0][0]
    
    #### STATS OPERATIONS ####
    def loadStat(self, username, key, stats):
        sql = "INSERT INTO STATS (username, key, stats) values ('%s', %s, '%s')" % (username, key, stats)
        return self.performWrite(sql)

    def getJoinedStat(self, prevKey, curKey):
        sql = """SELECT statsCur.username, statsPrev.stats, statsCur.stats
                    FROM stats statsPrev CROSS JOIN
                    stats statsCur
                    WHERE statsPrev.key = %s AND statsCur.key = %s 
                    AND statsPrev.username = statsCur.username""" % (prevKey, curKey)
        return self.performQuery(sql)


    def getFriendlyJoinedStat(self, prevKey, curKey):
        sql = """SELECT statsCur.username, statsPrev.stats, statsCur.stats, min(statsPrev.key)
                    FROM stats statsPrev CROSS JOIN
                    stats statsCur
                    WHERE statsPrev.key >= %s AND statsCur.key = %s 
                    AND statsPrev.username = statsCur.username
                    GROUP BY statsCur.username""" % (prevKey, curKey)
        return self.performQuery(sql)

    def getDupeCount(self):
        totalCountSql = """ SELECT count(*) FROM stats"""
        joinCountSql = """ SELECT count(*)
                    FROM stats statsPrev CROSS JOIN
                    stats statsCur
                    WHERE statsPrev.key = statsCur.key
                    AND statsPrev.username = statsCur.username"""

        return self.performQuery(totalCountSql)[0][0] - self.performQuery(joinCountSql)[0][0]

    #### BATTALION OPERATIONS ####
    #def createBattalion(self, name, guildId, channelId):
    #    sql = sql = "INSERT INTO BATTALIONS values ('%s', '%s', '%s') " % (name, guildId, channelId)
    #    return self.performWrite(sql)

    #def getBattalions(self):asdas
    #    sql = "SELECT * FROM BATTALIONS"
    #    return self.performQuery(sql)


    #### CHANNEL OPERATIONS ####
    def getChannels(self):
        sql = "SELECT * FROM CHANNELS"
        return self.performQuery(sql)

    def registerChannel(self, channelId):
        sql = "INSERT INTO CHANNELS values(%s)" % channelId
        return self.performWrite(sql)

    def clearChannels(self):
        sql = "DROP TABLE CHANNELS"
        self.performWrite(sql)
        newSql = """CREATE TABLE channels(channelId INTERGER)"""
        return self.performWrite(newSql)

    #### SCHEDULE OPERATIONS ####
    def getIndicies(self):
        sql = "SELECT * FROM iterator"
        return self.performQuery(sql)

    def getIndex(self, key):
        sql = "SELECT * FROM iterator WHERE key=%s" % key
        return self.performQuery(sql)
    
    def getKey(self):
        sql = "SELECT MAX(key) FROM iterator"
        maxKey = self.performQuery(sql)
        return maxKey[0][0]

    def incremementKey(self):
        curKey = self.getKey()
        nextKey = -1
        if(curKey == None):
            nextKey = 0
        else:
            nextKey = curKey + 1
        curTime = time.time()
        sql = "INSERT INTO iterator values (%s, %s)" % (nextKey, curTime)
        print(sql)
        self.performWrite(sql)
        return self.getKey()


    #### BANK OPERATIONS #### #TODO: THROW EXCEPTION IF ACCOUNT DOES NOT EXIST
    def getAccount(self, username):
        sql = f"""SELECT * FROM accounts where username = '{username}'"""
        return self.performQuery(sql)

    def hasAccount(self, username):
        account = self.getAccount(username)
        return len(account) == 1

    def balance(self, username):
        account = self.getAccount(username)
        return account[0][1]

    def deltaBalance(self, username, amount):
        curBalance = self.balance(username)
        newBalance = curBalance + amount
        sql = f"UPDATE accounts SET balance = {newBalance} where username='{username}'"
        return (self.performWrite(sql))        

    def transfer(self, sender, reciever, amount):
        self.deltaBalance(sender, -amount)
        self.deltaBalance(reciever, amount)
    
    def createAccount(self, username):
        sql = f"INSERT INTO accounts values ('{username}', 0)"
        return (self.performWrite(sql))    
    
    def accounts(self):
        sql = "SELECT * FROM accounts"
        return self.performQuery(sql)

    #### STANDARD OPERATIONS ####
    def performQuery(self, sql):
        conn = None
        try:
            print(sql)
            conn = self.createConnection()
            return conn.cursor().execute(sql).fetchall()
        finally:
            conn.close()

    def performWrite(self, sql):
        conn = None
        try:
            conn = self.createConnection()
            result = conn.cursor().execute(sql)
            conn.commit()
            return result
        finally:
            conn.close()

    def createConnection(self):
        return sqlite3.connect(self.filename)

    def createDatabaseTables(self):
        conn = None
        try:
            conn = self.createConnection()
            conn.cursor().execute("""CREATE TABLE users(username text PRIMARY KEY UNIQUE)""")
            #conn.cursor().execute("""CREATE TABLE battalions(battalion text PRIMARY KEY UNIQUE,
            #                    guild INTEGER,
            #                    channel INTEGER)""")
            conn.cursor().execute("""CREATE TABLE channels(channelId INTERGER)""")
            conn.cursor().execute("""CREATE TABLE stats(
                username TEXT,
                key INTEGER,
                stats MEDIUM BLOB,
                UNIQUE(username, key))""")
            conn.cursor().execute("""CREATE TABLE iterator(
                key INTEGER PRIMARY KEY,
                timestamp INTEGER
            )""")
            conn.commit()
        finally:
            conn.close()

    def createBankTables(self):
        conn = None
        try:
            conn = self.createConnection()
            conn.cursor().execute("""CREATE TABLE accounts(
                username TEXT,
                balance INTEGER,
                UNIQUE(username) ON CONFLICT FAIL)""")
            conn.commit()
        finally:
            conn.close()

    def createGameAccountMappingTable(self):
        conn = None
        try:
            conn = self.createConnection()
            conn.cursor().execute("""CREATE TABLE gameAccountMapping(
                username TEXT,
                platform TEXT,
                platformUsername TEXT,
                UNIQUE(platformUsername, platform) ON CONFLICT FAIL)""")
            conn.commit()
        finally:
            conn.close()

    def dropBankTables(self):
        conn = None
        try:
            conn = self.createConnection()
            conn.cursor().execute("""DROP TABLE accounts""")
            conn.commit()
        finally:
            conn.close()

    def dropMappingTable(self):
        conn = None
        try:
            conn = self.createConnection()
            conn.cursor().execute("""DROP TABLE gameAccountMapping""")
            conn.commit()
        finally:
            conn.close()
