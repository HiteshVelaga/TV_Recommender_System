import os
import pandas as pd
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

db_name = os.getenv('DB_NAME')
csv_path = os.path.join("data", "TV-2_processed.csv")

hd_quality_map = {"Other": 0, "HD": 1, "Full HD": 2, "Ultra HD 4K": 3}
def hd_to_quality(hd):
    try: return hd_quality_map[hd]
    except: return 0

mydb = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    passwd=os.getenv('DB_PASSWD')
)

mycursor = mydb.cursor()

print("Creating database if not exists")
mycursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
mydb.close()

mydb = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    passwd=os.getenv('DB_PASSWD'),
    db=db_name
)

mycursor = mydb.cursor()

print("Deleting table if exists")
mycursor.execute("DROP TABLE IF EXISTS TV")
mycursor.execute("DROP TABLE IF EXISTS QUALITY_VAL")

print("Creating table")
mycursor.execute("CREATE TABLE QUALITY_VAL(id INT PRIMARY KEY, hd VARCHAR(15))")
mycursor.execute("CREATE TABLE TV(id INT PRIMARY KEY AUTO_INCREMENT, brand VARCHAR(15), "
                    "ratings DECIMAL(5,2), speaker INT(1), size INT(1), quality INT(1), "
                    "hdmi INT(1), usb INT(1), cost INT(6), buy_from VARCHAR(1024), "
                    "img_url VARCHAR(512))")

print("Loading data from csv")
data = pd.read_csv(csv_path)
data["Quality"] = data["HD"].map(hd_to_quality)
data = data.drop("HD", axis=1)

print(data.head())
cols = "`, `".join([str(i) for i in data.columns.tolist()])

print("Loading data into database..... ", end='', flush=True)
for i, row in data.iterrows():
    mycursor.execute(f"INSERT INTO `TV` (`{cols}`) VALUES ({'%s, ' * (len(row) - 1)} %s)", tuple(row))
    
    if (i+1) % 100 == 0: mydb.commit()
mydb.commit()
print("Done Loading")

for key, value in hd_quality_map.items():
    mycursor.execute(f"INSERT INTO `QUALITY_VAL` (id, hd) VALUES (%s, %s)", (value, key))
mydb.commit()

print("Data in Database:")
mycursor.execute("SELECT * FROM TV")
for x in mycursor.fetchall():
  print(x)
print("\n\nData loaded into database")

print("Data in QUALITY_VAL Table:")
mycursor.execute("SELECT * FROM QUALITY_VAL")
for x in mycursor.fetchall():
  print(x)
print("Done")

