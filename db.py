import os
import json
import math
from dotenv import load_dotenv
import mysql.connector
from pprint import pprint

load_dotenv()

HDMI_PORT_VALUES = ["No HDMI Ports", "1 Port", "2 Ports", "3 Ports", "4 Ports"]
USB_PORT_VALUES = ["No USB Ports", "1 Port", "2 Ports", "3 Ports", "4 Ports"]

hd_quality_map = {"Other": 0, "HD": 1, "Full HD": 2, "Ultra HD 4K": 3}


def hd_to_quality(hd):
    try:
        return hd_quality_map[hd]
    except:
        return 0


db_name = os.getenv('DB_NAME')
mydb = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    passwd=os.getenv('DB_PASSWD'),
    db=db_name
)

# TODO: Change the function name


def output(speaker, size, hd, hdmi, usb):
    mycursor = mydb.cursor()
    query = "Select * from TV where `Speaker`=%s AND `Size`=%s AND `HD`=%s AND `HDMI`=%s AND `USB`=%s ORDER BY `Cost`, `Ratings` LIMIT 3"

    inputs = (speaker, size, hd, hdmi, usb)
    mycursor.execute(query, inputs)
    myresult = mycursor.fetchall()
    tv1 = {"Brand":  myresult[0][0],
           "Ratings": myresult[0][1],
           "Speaker": myresult[0][2],
           "Size": myresult[0][3],
           "Quality": myresult[0][4],
           "HDMI": myresult[0][5],
           "USB": myresult[0][6],
           "Cost": myresult[0][7]}

    tv2 = {"Brand": myresult[1][0],
           "Ratings": myresult[1][1],
           "Speaker": myresult[1][2],
           "Size": myresult[1][3],
           "Quality": myresult[1][4],
           "HDMI": myresult[1][5],
           "USB": myresult[1][6],
           "Cost": myresult[1][7]}

    tv3 = {"Brand": myresult[2][0],
           "Ratings": myresult[2][1],
           "Speaker": myresult[2][2],
           "Size": myresult[2][3],
           "Quality": myresult[2][4],
           "HDMI": myresult[2][5],
           "USB": myresult[2][6],
           "Cost": myresult[2][7]}

    return tv1, tv2, tv3


def get_user_pick(brand, cost, hdmi, quality, rating, size, speaker, usb):
    quality = hd_to_quality(quality)
    cursor = mydb.cursor(dictionary=True)
    query = f"""with diff_table
              as
              (
                  select id,
                      abs(cost-{cost}) diff_cost,
                      abs(hdmi-{hdmi}) diff_hdmi, 
                      abs(quality-{quality}) diff_quality,
                      abs(ratings-{rating}) diff_rating, 
                      abs(size-{size}) diff_size, 
                      abs(speaker-{speaker}) diff_speaker, 
                      abs(usb-{usb}) diff_usb
                  from tv
                  where brand='{brand}'
              ) 
              select tv.id, 
                  tv.brand,
                  tv.cost,
                  tv.hdmi,
                  quality_val.hd quality,
                  tv.ratings,
                  tv.size,
                  tv.speaker,
                  tv.usb,
                  tv.buy_from,
                  tv.img_url,
                  sqrt(diff_hdmi*diff_hdmi + diff_rating*diff_rating + diff_size*diff_size + diff_speaker*diff_speaker + diff_usb*diff_usb + diff_cost*diff_cost) diff
              from diff_table
              join tv
              on diff_table.id = tv.id
              join quality_val
              on tv.quality = quality_val.id
              order by diff
              limit 1;"""
    cursor.execute(query)
    result = cursor.fetchall()[0]
    result["ratings"] = int(result["ratings"])
    return result


def get_optimum_pick(brand, cost, hdmi, quality, rating, size, speaker, usb, limit=3):
    quality = hd_to_quality(quality)
    cursor = mydb.cursor(dictionary=True)
    query = f"""with diff_table
              as
              (
                  select id,
                      abs(cost-{cost}) diff_cost,
                      abs(hdmi-{hdmi}) diff_hdmi, 
                      abs(quality-{quality}) diff_quality,
                      abs(ratings-{rating}) diff_rating, 
                      abs(size-{size}) diff_size, 
                      abs(speaker-{speaker}) diff_speaker, 
                      abs(usb-{usb}) diff_usb
                  from tv
              ) 
              select tv.id, 
                  tv.brand,
                  tv.cost,
                  tv.hdmi,
                  quality_val.hd quality,
                  tv.ratings,
                  tv.size,
                  tv.speaker,
                  tv.usb,
                  tv.buy_from,
                  tv.img_url,
                  sqrt(diff_hdmi*diff_hdmi + diff_rating*diff_rating + diff_size*diff_size + diff_speaker*diff_speaker + diff_usb*diff_usb + diff_cost*diff_cost) diff
              from diff_table
              join tv
              on diff_table.id = tv.id
              join quality_val
              on tv.quality = quality_val.id
              order by diff
              limit {limit};"""
    cursor.execute(query)
    result = cursor.fetchall()
    most_opt = result[0]
    most_opt["ratings"] = int(most_opt["ratings"])
    more = [x for x in result[1:]]
    for x in more: x["ratings"] = int(x["ratings"])

    return (most_opt, more)


def menu_options():
    with open(os.path.join("json", "menu.json")) as f:
        menus = json.load(f)

    cursor = mydb.cursor()

    cursor.execute("select distinct brand from tv order by brand")
    brands = [{"key": x[0], "value": f"{x[0][0].upper()}{x[0][1:]}"}
              for x in cursor.fetchall()]
    menus[0]["options"] = brands

    cursor.execute("select distinct size from tv order by size")
    sizes = [{"key": x[0], "value": f"{x[0]} Inch"} for x in cursor.fetchall()]
    menus[1]["options"] = sizes

    cursor.execute("select hd from quality_val where id > 0 order by id desc")
    hd = [{"key": x[0], "value": x[0]} for x in cursor.fetchall()]
    menus[2]["options"] = hd

    cursor.execute("select max(ratings) from tv")
    ratings = [{"key": x, "value": "🌟"*x}
               for x in range(1, math.ceil(cursor.fetchall()[0][0])+1)]
    menus[3]["options"] = ratings

    cursor.execute("select distinct hdmi from tv order by hdmi")
    hdmi = [{"key": x[0], "value": HDMI_PORT_VALUES[x[0]]}
            for x in cursor.fetchall()]
    menus[4]["options"] = hdmi

    cursor.execute("select distinct usb from tv order by usb")
    usb = [{"key": x[0], "value": USB_PORT_VALUES[x[0]]}
           for x in cursor.fetchall()]
    menus[5]["options"] = usb

    cursor.execute("select distinct speaker from tv order by speaker")
    hd = [{"key": x[0], "value": f"{x[0]}W"} for x in cursor.fetchall()]
    menus[6]["options"] = hd
    return menus


if __name__ == "__main__":
    # pprint(menu_options())
    dict = {'brand': 'samsung',
            'cost': 109132,
            'hdmi': 4,
            'quality': 'ultra hd 4k',
            'rating': 5,
            'size': 65,
            'speaker': 60,
            'usb': 3}
    get_user_pick(**dict)
