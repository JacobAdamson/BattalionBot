import unittest
from battalions import battalion
import os
from infrastructure.db import SqlLiteDom

class TestBattalion(unittest.TestCase):
    def setUp(self):
        self.filename = "test_database.db"
        open(self.filename, "w").close()
        self.dom = SqlLiteDom(self.filename)
        self.dom.createBattalionTables()
        self.dom.createDatabaseTables()

    def tearDown(self):
        os.remove(self.filename)

    def testCreateBattalion(self):
        battalion.createBattalion(self.dom, "jacob", "ugly")
        battalions = battalion.getBattalions(self.dom)
        self.assertEquals(battalions[0][0], "ugly")
        permission = battalion.getUserPermission(self.dom, "jacob", "ugly")
        self.assertEquals(permission[0][0], "GENERAL")
        userBattalions = battalion.getUserBattalionPermissions(self.dom, "jacob")
        self.assertEquals(userBattalions[0], ("jacob", "ugly", "GENERAL"))


if __name__ == '__main__':
    unittest.main()