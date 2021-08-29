import os
from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
import re

URL = "https://www.flipkart.com/search?q=tv&sid=ckf%2Cczl&as=on&as-show=on&otracker=AS_QueryStore_OrganicAutoSuggest_1_2_na_na_na&otracker1=AS_QueryStore_OrganicAutoSuggest_1_2_na_na_na&as-pos=1&as-type=RECENT&suggestionId=tv%7CTVs&requestId=3ee7e2ac-b845-4a0c-a075-232968460b29&as-backfill=on&page="
csv_file = os.path.join('data', 'TV-2.csv')
tv_data = []

for i in range(72):
    url = f"{URL}{i}"
    print(f"{i+1} - {url}")
    with urlopen(url) as client:
        soup = BeautifulSoup(client.read(), 'html.parser')
    
    items = soup.find_all("div", { "class": "_1YokD2 _3Mn1Gg"})[1]\
                .find_all("div", { "class": "_1AtVbE col-12-12"})
    
    for item in items:
        try:
            name = item.find("div", {"class": "_4rR01T"}).text
            brand = name.split(' ')[0]
            size = re.search("((\d{1,2}) inch)", name, re.IGNORECASE).groups()[1]
            rating = item.find("div", {"class": "_3LWZlK"}).text
            cost = item.find("div", {"class": "_30jeq3 _1_WHN1"}).text[1:].replace(',', '')
            buy_from = f'https://www.flipkart.com{item.find("a", {"class": "_1fQZEK"})["href"]}'
            
            with urlopen(buy_from) as buy_from_c:
                tv_soup = BeautifulSoup(buy_from_c.read(), 'html.parser')
            img_url = tv_soup.find("div", {"class": "CXW8mj _3nMexc"}).find("img")["srcset"].split(",")[0].split(" ")[0]

            spec_list = item.find("ul", {"class": "_1xgFaf"}).find_all("li", {"class": "rgWa7D"})

            item_data = {'Brand': brand, "Ratings": rating, "Speaker": 0, "Size": size, 
                    "HD": "Other", "HDMI": 0, "USB": 0, "Cost": cost, "buy_from": buy_from, 
                    "img_url": img_url}

            for spec in spec_list:
                if('Full HD' in spec.text):
                    item_data["HD"] = 'Full HD'
                elif('HD Ready' in spec.text):
                    item_data["HD"] = 'HD'
                elif('Ultra HD (4K)' in spec.text):
                    item_data["HD"] = 'Ultra HD 4K'
                elif('Ultra HD (8K)' in spec.text):
                    item_data["HD"] = 'Ultra HD 8K'
            
                if('Speaker' in spec.text):
                    try: item_data["Speaker"] = int(re.search("((\d{1,2}) W)", spec.text, re.IGNORECASE).groups()[1])
                    except: pass

                if('HDMI' in spec.text):
                    try: item_data["HDMI"] = int(re.search("((\d) x HDMI)", spec.text, re.IGNORECASE).groups()[1])
                    except: pass
                
                if('USB' in spec.text):
                    try: item_data["USB"] = int(re.search("((\d) x USB)", spec.text, re.IGNORECASE).groups()[1])
                    except: pass
            tv_data.append(item_data)
        except AttributeError:
            continue

TV_data = pd.DataFrame(tv_data)
TV_data.to_csv(csv_file, index=False)
print(f"Saved Dataframe of shape: {TV_data.shape} to {csv_file}")
