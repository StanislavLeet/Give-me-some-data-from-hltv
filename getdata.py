import time
import json
import requests
import pandas as pd
from lxml import html
from tqdm.auto import tqdm
import utils


links_to_matches = []
for i in tqdm(range(54)):
    url = 'https://www.hltv.org/results?offset={}&startDate=2019-04-05&endDate=2020-04-05&matchType=Online'.format(int(i*100))
    links_to_matches += utils.GimeMeMatchLinks(url)


data = dict()
count = 0
for link in tqdm(links_to_matches):
    url = 'https://www.hltv.org{}'.format(link)
    mapstat = utils.GiveMeMatches(url)
    
    if len(mapstat) == 0:
        continue
        
    for stat in mapstat:
        url = 'https://www.hltv.org{}'.format(stat)
        OneMatch = utils.GiveInfoFromMatch(url, stat)
        
        
        if len(OneMatch.keys()) > 1:
            data[stat.split('/')[-2]] = dict()
            data[stat.split('/')[-2]]['url'] = url
            data[stat.split('/')[-2]]['Team 1'] = OneMatch['Team 1']
            data[stat.split('/')[-2]]['Team 2'] = OneMatch['Team 2']
            data[stat.split('/')[-2]]['Team 1 score'] = OneMatch['Team 1 score']
            data[stat.split('/')[-2]]['Team 2 score'] = OneMatch['Team 2 score']
            data[stat.split('/')[-2]]['First CT'] = OneMatch['First CT']
            data[stat.split('/')[-2]]['map'] = OneMatch['map']
            data[stat.split('/')[-2]]['side dynamic'] = OneMatch['side dynamic']
            
    if count % 50 == 0 and count > 0:
        with open('CSjson.json', 'w') as f:
            f.write(json.dumps(data))

    count += 1

with open('CSjson.json', 'w') as f:
    f.write(json.dumps(data))