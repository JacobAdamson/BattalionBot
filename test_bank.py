import unittest
import bank
import os
import json
from db import SqlLiteDom

class TestBank(unittest.TestCase):
    def setUp(self):
        self.filename = "test_database.db"
        open(self.filename, "w").close()
        self.dom = SqlLiteDom(self.filename)
        self.dom.createBankTables()

    def tearDown(self):
        os.remove(self.filename)

    def testAward(self):
        self.dom.createAccount("jacob")
        bank.award(self.dom, "jacob", 100)
        balance = bank.balance(self.dom, "jacob")
        self.assertEquals(balance, 100)

    def testTransfer(self):
        self.dom.createAccount("jacob")
        self.dom.createAccount("noah")
        bank.award(self.dom, "jacob", 100)
        bank.transfer(self.dom, "jacob", "noah", 25)
        self.assertTrue(75, bank.balance(self.dom, "jacob"))
        self.assertTrue(25, bank.balance(self.dom, "noah"))

if __name__ == '__main__':
    unittest.main()