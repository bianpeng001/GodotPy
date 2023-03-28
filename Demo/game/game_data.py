#
# 2023年2月9日 bianpeng
#
import os
import sqlite3
import json

# 游戏存档
class GameData:
    def __init__(self):
        self.start_year = 181
        self.play_time = 0
        
        self.cur_year = self.get_cur_year()
        self.cur_month = 1

        self.player_list = []
        self.hero_list = []
        self.city_list = []

    def load(self, path):
        pass

    def save(self, path):
        if os.path.exists(path):
            os.remove(path)
            
        conn = sqlite3.connect(path)
        
        cursor = conn.cursor()
        cursor.execute('''
CREATE TABLE CITY (
    ID INT PRIMARY KEY NOT NULL,
    NAME TEXT NOT NULL,
    X INT,
    Y INT,
);
''')
        cursor.execute('''
CREATE TABLE HERO (
ID INT PRIMARY KEY NOT NULL,
NAME TEXT NOT NULL,
BORN_YEAR INT,
CITY_ID INT references CITY(ID),
);
''')
        cursor.execute('''
CREATE TABLE TROOP (
ID INT PRIMARY KEY NOT NULL,
NAME TEXT NOT NULL,
CHIEF_HERO_ID INT references HERO(ID)
HERO_LIST INT ARRAY[9],
);
''')
        conn.commit()
        
        conn.close()

    def get_cur_year(self):
        return self.start_year + int(self.play_time / (86400*365))



