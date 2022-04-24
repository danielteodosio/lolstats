import requests
import time
import json
from datetime import datetime


MATCH_BY_MATCHID_RIOT_ENDPOINT = "https://americas.api.riotgames.com/lol/match/v5/matches/{matchId}"
MATCHS_BY_PUUID_RIOT_ENDPOINT = "https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"

def mergeParametersPathOnURL(baseURL, pathHolder, realPath):
    return str(baseURL).replace(pathHolder, realPath)

def getMySelfMatchStats(myPuuid, riotMatchDTO):
    particpants = riotMatchDTO['info']['participants']
    for participant in particpants:
        if participant['puuid'] == myPuuid:
            return participant
    return -1

def getMyComradesMatchStats(myTeamId, riotMatchDTO):
    comrades = []
    particpants = riotMatchDTO['info']['participants']
    for participant in particpants:
        if participant['teamId'] == myTeamId:
            comrades.append(participant)
    return comrades

def getMyDesiredStats(myPuuid ,riotMatchDTO):
    desiredStats = {}
    riotParticipantDTO = getMySelfMatchStats(myPuuid, riotMatchDTO)

    desiredStats['championName'] = riotParticipantDTO['championName']
    desiredStats['kills'] = riotParticipantDTO['kills']
    desiredStats['deaths'] = riotParticipantDTO['deaths']
    desiredStats['assists'] = riotParticipantDTO['assists']
    desiredStats['damageDealtToTurrets'] = riotParticipantDTO['damageDealtToTurrets']
    desiredStats['goldEarned'] = riotParticipantDTO['goldEarned']
    desiredStats['magicDamageDealtToChampions'] = riotParticipantDTO['magicDamageDealtToChampions']
    desiredStats['magicDamageTaken'] = riotParticipantDTO['magicDamageTaken']
    desiredStats['physicalDamageDealtToChampions'] = riotParticipantDTO['physicalDamageDealtToChampions']
    desiredStats['physicalDamageTaken'] = riotParticipantDTO['physicalDamageTaken']
    desiredStats['totalDamageDealtToChampions'] = riotParticipantDTO['totalDamageDealtToChampions']
    desiredStats['totalDamageTaken'] = riotParticipantDTO['totalDamageTaken']
    desiredStats['timeCCingOthers'] = riotParticipantDTO['timeCCingOthers']
    desiredStats['totalTimeSpentDead'] = riotParticipantDTO['totalTimeSpentDead']
    desiredStats['totalMinionsKilled'] = riotParticipantDTO['totalMinionsKilled']
    desiredStats['trueDamageDealtToChampions'] = riotParticipantDTO['trueDamageDealtToChampions']
    desiredStats['trueDamageTaken'] = riotParticipantDTO['trueDamageTaken']

    #begin derivate attributes
    if desiredStats['deaths'] != 0:
        desiredStats['KDA'] = (int(desiredStats['kills']) + int(desiredStats['assists'])) / int(desiredStats['deaths'])
    else:
        desiredStats['KDA'] = (int(desiredStats['kills']) + int(desiredStats['assists']))

    myTeamId = riotParticipantDTO['teamId']
    myComrades = getMyComradesMatchStats(myTeamId, riotMatchDTO)

    totalPhisicalDamageDealt = 0
    totalMagicalDamageDealt = 0
    totalTotalDamageDealt = 0
    totalTrueDamageDealt = 0

    totalPhisicalDamageTaken = 0
    totalMagicalDamageTaken = 0
    totalTotalDamageTaken = 0
    totalTrueDamageTaken = 0

    for comrade in myComrades:
        totalPhisicalDamageDealt += int(comrade['physicalDamageDealtToChampions'])
        totalMagicalDamageDealt += int(comrade['magicDamageDealtToChampions'])
        totalTotalDamageDealt += int(comrade['totalDamageDealtToChampions'])
        totalTrueDamageDealt += int(comrade['trueDamageDealtToChampions'])
        totalPhisicalDamageTaken += int(comrade['physicalDamageTaken'])
        totalMagicalDamageTaken += int(comrade['magicDamageTaken'])
        totalTotalDamageTaken += int(comrade['totalDamageTaken'])
        totalTrueDamageTaken += int(comrade['trueDamageTaken'])

    desiredStats['relativePhisicalDamageDealt'] = int(desiredStats['physicalDamageDealtToChampions']) / float(totalPhisicalDamageDealt + 0.000001)
    desiredStats['relativeMagicalDamageDealt'] = int(desiredStats['magicDamageDealtToChampions']) / float(totalMagicalDamageDealt + 0.000001)
    desiredStats['relativeTotalDamageDealt'] = int(desiredStats['totalDamageDealtToChampions']) / float(totalTotalDamageDealt + 0.000001)
    desiredStats['relativeTrueDamageDealt'] = int(desiredStats['trueDamageDealtToChampions']) / float(totalTrueDamageDealt + 0.000001)

    desiredStats['relativePhisicalDamageTaken'] = int(desiredStats['physicalDamageTaken']) / float(totalPhisicalDamageTaken + 0.000001)
    desiredStats['relativeMagicalDamageTaken'] = int(desiredStats['magicDamageTaken']) / float(totalMagicalDamageTaken + 0.000001)
    desiredStats['relativeTotalDamageTaken'] = int(desiredStats['totalDamageTaken']) / float(totalTotalDamageTaken + 0.000001)
    desiredStats['relativeTrueDamageTaken'] = int(desiredStats['trueDamageTaken']) / float(totalTrueDamageTaken + 0.000001)
    #end derivate attributes

    desiredStats['gameDurationSec'] = riotMatchDTO['info']['gameDuration']
    desiredStats['dateCreationTimeStamp'] = riotMatchDTO['info']['gameCreation']
    desiredStats['dateCreationDate'] = str(datetime.fromtimestamp(int(desiredStats['dateCreationTimeStamp']/1000)))

    desiredStats['win'] = riotParticipantDTO['win']

    return desiredStats

def getListOfMatchsIdsByPuuid(puuid, key):
    payload = {'type':'ranked', 'start': 0, 'count': 100, 'api_key': key}
    obj = requests.get(mergeParametersPathOnURL(MATCHS_BY_PUUID_RIOT_ENDPOINT, "{puuid}", puuid), params=payload)
    return obj.json()


def getMatchByMatchId(matchId, key):
    payload = {'api_key': key}
    obj = requests.get(mergeParametersPathOnURL(MATCH_BY_MATCHID_RIOT_ENDPOINT, "{matchId}", matchId), params=payload)
    riotMatchDTO = obj.json()
    return riotMatchDTO

def getMyMatchsDesiredStats(puuid, key):
    myMatchsDesiredStats = {}
    listOfMatchsStats = []
    listOfMatchs = getListOfMatchsIdsByPuuid(puuid, key)
    totalRequests = len(listOfMatchs)
    completedRequests = 1
    for matchId in listOfMatchs:
        riotMatchDTO = getMatchByMatchId(matchId,key)
        if len(riotMatchDTO) < 2:
            print("request: " + str(completedRequests) + " falhou")
            completedRequests = completedRequests + 1
            continue
        matchDesiredStats = getMyDesiredStats(puuid, riotMatchDTO)
        listOfMatchsStats.append(matchDesiredStats)
        print(str(completedRequests) + " of " + str(totalRequests) + " completed ...")
        completedRequests = completedRequests + 1
        time.sleep(0.5)
    myMatchsDesiredStats['matchStats'] = listOfMatchsStats
    return myMatchsDesiredStats



print("Chave atual: ")
key = input()
print("PUUID: ")
puuid = input()
print("local ou nome do json gerado: ")
nameJson = input()

myMatchsDesiredStats = getMyMatchsDesiredStats(puuid, key)
with open(nameJson + ".json", "w") as file:
    json.dump(myMatchsDesiredStats, file)






















