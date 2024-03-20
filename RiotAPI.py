import requests
import sys
import json
import time

API_KEY = "RGAPI-6bcf1eea-7d70-4039-9413-cd8234eba523"
REGION = "na1"
RATE_LIMIT = 0.85

def formatAndCallURL(endpoint, options, region=REGION):
    url = f"https://{region}.api.riotgames.com/{endpoint}?{options}api_key={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        sys.exit(1)
    return response.json()

def getChallengers():
    endpoint = "tft/league/v1/challenger"
    options = "queue=RANKED_TFT&"
    data = formatAndCallURL(endpoint, options)

    challengers = dict()
    for summoner in data['entries']:
        challengers[summoner['summonerName']] = summoner['summonerId']
    return challengers

def getPUUIDs(challengers):
    PUUIDs = dict()
    for summoner, id in challengers.items():
        endpoint = f"tft/league/v1/entries/by-summoner/{id}"
        options = ""
        data = formatAndCallURL(endpoint, options)
        time.sleep(RATE_LIMIT)
        PUUIDs[summoner] = data[0]['puuid']
    return PUUIDs

def storePUUIDs():
    PUUIDs = getPUUIDs(getChallengers())
    with open('data/PUUID.json', 'w') as file:
        json.dump(PUUIDs, file)

def storeMatches():
    with open('data/PUUID.json', 'r') as file:
        PUUIDs = json.load(file)

        for summoner, id in PUUIDs.items():
            endpoint = f"tft/match/v1/matches/by-puuid/{id}/ids"
            options = "start=0&count=20&"
            matches = formatAndCallURL(endpoint, options, "americas")

            for match_id in matches:
                endpoint = f"tft/match/v1/matches/{match_id}"
                options = ""
                match = formatAndCallURL(endpoint, options, "americas")
                time.sleep(RATE_LIMIT)

                with open('data/MATCH.json', 'a') as file:
                    json.dump(match, file)
                    file.write('\n')