import time
import json
import requests
import pandas as pd
from lxml import html
from tqdm.auto import tqdm
import utils


links_to_matches = []
for i in tqdm(range(54)):
    url = 'https://www.hltv.org/results?offset={}&startDate=2019-04-05&endDate=2020-04-05&matchType=Online'.format(i*100)
    links_to_matches += utils.get_match_links(url)


data = dict()
count = 0
for link in tqdm(links_to_matches):
    url = 'https://www.hltv.org{}'.format(link)
    mapstat = utils.get_matches(url)
    
    if len(mapstat) == 0:
        continue
        
    for stat in mapstat:
        url = 'https://www.hltv.org{}'.format(stat)
        OneMatch = utils.get_info_from_match(url, stat)
        match_id = stat.split('/')[-2]
        
        if len(OneMatch.keys()) > 1:
            data[match_id] = dict()
            data[match_id]['url'] = url
            for key in OneMatch:
                data[match_id][key] = OneMatch[key]
            
    if count % 50 == 0 and count > 0:
        with open('CSjson.json', 'w') as f:
            f.write(json.dumps(data))

    count += 1

with open('CSjson.json', 'w') as f:
    f.write(json.dumps(data))