import requests
import json


def storeAndIncrement(dom):
    key = dom.incremementKey()
    storeData(dom, key)
    return key


def storeData(dom, key):
    users = dom.getUsers()
    for user in users:
        data = queryBfTracker(user[0])
        stringifiedData:str = json.dumps(data)
        dom.loadStat(user[0], key, stringifiedData)

def createLiveStat(dom):
    users = dom.getUsers()
    liveStat = []
    for user in users:
        data = queryBfTracker(user[0])
        liveStat.append([user[0], json.dumps(data)])
    return liveStat

def queryBfTracker(username): 
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36'}
    return requests.get('https://api.tracker.gg/api/v2/bfv/standard/profile/psn/' + username + '?forceCollect=true', headers=headers).json()