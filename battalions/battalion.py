from infrastructure.db import SqlLiteDom


def getBattalions(dom: SqlLiteDom):
    return dom.getBattalions()


def getUserPermission(dom: SqlLiteDom, actor, battalionName):
    return dom.getUserBattalionPermission(actor, battalionName)


def getUserBattalionPermissions(dom: SqlLiteDom, actor):
    return dom.getUserBattalions(actor)


def createBattalion(dom: SqlLiteDom, actor, battalionName):
    dom.createBattalion(battalionName)
    dom.setUserPermissionOnBattalion(actor, battalionName, "GENERAL")


def discharge(dom: SqlLiteDom, actor, battalionName, platformId):
    permission = dom.getUserBattalionPermission(actor, battalionName)
    if len(permission) > 1 and permission[0][0] == "GENERAL" or permission[0][0] == "OFFICER":
        dom.dischargeUser(battalionName, platformId)
    #THROW EXCEPTION


def enlist(dom: SqlLiteDom, actor, battalionName, platformId):
    permission = dom.getUserBattalionPermission(actor, battalionName)
    if len(permission) > 1 and permission[0][0] == "GENERAL" or permission[0][0] == "OFFICER":
        dom.enlistUser(battalionName, platformId)
    # THROW EXCEPTION


def makeOfficer(dom: SqlLiteDom, actor, battalionName, userId):
    permission = dom.getUserBattalionPermission(actor, battalionName)
    if len(permission) > 1 and permission[0][0] == "GENERAL":
        dom.setUserPermissionOnBattalion(userId, battalionName, "")
    #THROW EXCEPTION


def makeGeneral(dom: SqlLiteDom, actor, battalionName, userId):
    permission = dom.getUserBattalionPermission(actor, battalionName)
    if len(permission) > 1 and permission[0][0] == "GENERAL":
        dom.setUserPermissionOnBattalion(userId, battalionName, "GENERAL")
    # THROW EXCEPTION