from typing import List

class SingleStat:
    segments: List[str] = None
    statkey: str = None

    def __init__(self, segment, statkey):
        if segment == "ground":
            self.segments = ["assault", "medic", "support", "recon"]
        else:
            self.segments = [segment]
        self.statkey = statkey

    @staticmethod
    def createFromString(statString):
        splitStat = statString.split(".")
        if len(splitStat) == 1:
            return SingleStat("overview", splitStat[0])
        elif len(splitStat) == 2:
            return SingleStat(splitStat[0], splitStat[1])


class StatDefinition:  # create enums
    stat: SingleStat = None
    denominatorStat: SingleStat = None

    def __init__(self, stat, denominatorStat):
        self.stat = stat
        self.denominatorStat = denominatorStat

    @staticmethod
    def createFromString(statString):
        splitStat = statString.split("/")
        if len(splitStat) == 1:
            return StatDefinition(SingleStat.createFromString(splitStat[0]), None)
        elif len(splitStat) == 2:
            return StatDefinition(SingleStat.createFromString(splitStat[0]),
                                  SingleStat.createFromString(splitStat[1]))


class LeaderboardConfig:
    statDefinitions: List[StatDefinition] = None
    numRows: int = None

    def __init__(self, statDefinitions, numRows):
        self.statDefinitions = statDefinitions
        self.numRows = numRows

    @staticmethod
    def createFromString(statString, numRows):
        statDefinitions = []
        splitStatDefString = statString.split(" ")
        for statDefString in splitStatDefString:
            statDefinitions.append(StatDefinition.createFromString(statDefString))
        return LeaderboardConfig(statDefinitions, numRows)


class ReportConfig:
    battalion: List[str] = None
    users: List[str] = None
    startIndex: int = None
    endIndex: int = None