import os
from bs4 import BeautifulSoup
from urllib.request import urlopen as urlReq
import pandas as pd

URL = "https://www.flipkart.com/search?q=tv&sid=ckf%2Cczl&as=on&as-show=on&otracker=AS_QueryStore_OrganicAutoSuggest_1_2_na_na_na&otracker1=AS_QueryStore_OrganicAutoSuggest_1_2_na_na_na&as-pos=1&as-type=RECENT&suggestionId=tv%7CTVs&requestId=3ee7e2ac-b845-4a0c-a075-232968460b29&as-backfill=on&page="
TV = []
r = 0
TV_Brand = []
TV_Ratings = []
TV_size = []
TV_HD = []
TV_speakers = []
TV_hdmi = []
TV_usb = []
TV_cost = []
TV_buy_from = []


for i in range(1):
    url = f"{URL}{i}"
    print(f"{i+1} - {url}")
    Client = urlReq(url)
    html_data = Client.read()
    Client.close()
    soup = BeautifulSoup(html_data, 'html.parser')

    # Brand of TV
    names = soup.find_all("div", {"class": "_4rR01T"})
    for name in names:
        TV_Brand.append(name.text.split(' ')[0])

    # TV ratings
    ratings = soup.find_all("div", {"class": "_3LWZlK"})
    for rating in ratings:
        if(r < len(TV_Brand)):
            TV_Ratings.append(float(rating.text))
            r += 1

    # TV size
    sizes = soup.find_all("div", {"class": "_4rR01T"})
    for size in sizes:
        size_of_tv = size.text[int(size.text.find("("))+1:int(size.text.find(")"))]
        try:
            if(('inch' in size_of_tv) or 'cm' in size_of_tv):
                size_of_tv = size_of_tv.split()[0]
            else:
                size_of_tv = 0
            TV_size.append(float(size_of_tv))
        except ValueError as e:
            TV_size.append(0)

    # HD
    HDs = soup.find_all("ul", {"class": "_1xgFaf"})
    for HD in HDs:
        for li in HD.find_all("li", {"class": "rgWa7D"}):
            if('Full HD' in li.text):
                TV_HD.append('Full HD')
            if('HD Ready' in li.text):
                TV_HD.append('HD')
            if('Ultra HD (4K)' in li.text):
                TV_HD.append('Ultra HD 4K')
            if('Ultra HD (8K)' in li.text):
                TV_HD.append('Ultra HD 8K')
            else:
                TV_HD.append('Other')

    # Speakers
    speakers = soup.find_all("ul", {"class": "_1xgFaf"})
    for speaker in speakers:
        for li in speaker.find_all("li", {"class": "rgWa7D"}):
            if('Speaker' in li.text):
                try:
                    TV_speakers.append(int(li.text.lower().split('w')[0]))
                except:
                    TV_speakers.append(0)

    # Hdmi
    HDMIS = soup.find_all("ul", {"class": "_1xgFaf"})
    for HDMI in HDMIS:
        for li in HDMI.find_all("li", {"class": "rgWa7D"}):
            if('HDMI' in li.text):
                TV_hdmi.append(int(li.text.split('x')[0]))

    # USB
    USBS = soup.find_all("ul", {"class": "_1xgFaf"})
    for USB in USBS:
        for li in USB.find_all("li", {"class": "rgWa7D"}):
            if('USB' in li.text):
                TV_usb.append(int(li.text.split('|')[-1].split('x')[0].strip()))
                break

    # Cost of TV
    costs = soup.find_all("div", {"class": "_30jeq3 _1_WHN1"})
    for cost in costs:
        price = cost.text.split('₹')[1]
        price = price.replace(',', '')
        TV_cost.append(int(price))
    
    print(f"{i+1} - len(TV_Brand): {len(TV_Brand)}; len(TV_Ratings): {len(TV_Ratings)}; "
          f"len(TV_size): {len(TV_size)}; len(TV_HD): {len(TV_HD)}; len(TV_speakers): {len(TV_speakers)}; "
          f"len(TV_hdmi): {len(TV_hdmi)}; len(TV_usb): {len(TV_usb)}; len(TV_cost): {len(TV_cost)}\n"
          f"len(TV_buy_from): {len(TV_buy_from)}")
    print("TV_HD:", TV_HD, end='\n\n')

print("TV_Brand:", TV_Brand, end='\n\n')
print("TV_Ratings:", TV_Ratings, end='\n\n')
print("TV_size:", TV_size, end='\n\n')
print("TV_HD:", TV_HD, end='\n\n')
print("TV_speakers:", TV_speakers, end='\n\n')
print("TV_hdmi:", TV_hdmi, end='\n\n')
print("TV_usb:", TV_usb, end='\n\n')
print("TV_cost:", TV_cost, end='\n\n')


# creatinf dataframe
for Brand, Ratings, Speaker, Size, HD, HDMI, USB, Cost in zip(TV_Brand, TV_Ratings, TV_speakers, TV_size, TV_HD, TV_hdmi, TV_usb, TV_cost):
    TV.append({'Brand': Brand, 'Ratings': Ratings, 'Speaker': Speaker,
               'Size': Size, 'HD': HD, 'HDMI': HDMI, 'USB': USB, 'Cost': Cost})


csv_file = os.path.join('data', 'TV-2.csv')
TV_data = pd.DataFrame(TV)
TV_data.to_csv(csv_file, index=False)

print(f"Saved Dataframe of shape: {TV_data.shape} to {csv_file}")
