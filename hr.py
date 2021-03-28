import loader
import analyzer
import bank


def processLastPerformance(dom):
    key = dom.getKey()
    return processPerformance(dom, key - 1, key)


def processPerformanceSince(dom, since):
    key = dom.getKey()
    return processPerformance(dom, key - since, key)


def processPerformance(dom, startKey, endKey):
    joinedStatLine = dom.getFriendlyJoinedStat(startKey, endKey)
    tableData = analyzer.generateTableData(joinedStatLine, ["wins", "kills"], ["overview"], False)
    return awardTokensToGameAccounts(dom, tableData)


def generateReports(payInfoRows, client):
    # analyzer.sortAndFilter(payInfoRows, 0, -1, False)
    presentationInfoRows = []
    for row in payInfoRows:
        accountName = "acc:"
        # if(client != None):
        #    accountName = await client.fetch_user(row[0]).name
        presentationInfoRows.append([accountName, row[1][0:8], "", ""])
        presentationInfoRows.append(["type", "qntity", "rate", "tkns"])
        totalPay = 0
        for payItem in row[2]:
            presentationInfoRows.append(payItem)
            totalPay = totalPay + payItem[3]
        presentationInfoRows.append(["", "", "tot:", totalPay])
    table = analyzer.createTable(["UGLY", "PAY", "STMT", ""], presentationInfoRows)
    return "```" + table.draw() + "```"


def awardTokensToGameAccounts(dom, table):
    payInfo = []
    for row in table:
        (platformUsername, wins, kills) = row
        account = dom.getAccountForPlatformUsername("psn", platformUsername)
        if account is not None:
            bank.award(dom, account, wins)
            bank.award(dom, account, kills * .01)
            payInfo.append(
                [account, platformUsername, [("wins", wins, 1, wins * 1), ("kills", kills, .01, kills * .01)]])
    return payInfo


def conscript(dom, username, platform, platformUsername):
    dom.conscriptUser(username, platform, platformUsername)
    if not dom.userExists(platformUsername):
        dom.enlistUser(platformUsername)
    if not dom.hasAccount(username):
        dom.createAccount(username)
