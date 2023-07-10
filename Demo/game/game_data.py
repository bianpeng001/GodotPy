#
# 2023年2月9日 bianpeng
#
import os
import sqlite3
import json

from game.game_mgr import game_mgr

#
# 游戏存档
#
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

    def do_save(self, conn):
        cursor = conn.cursor()
# PLAYER
        cursor.execute('''
CREATE TABLE PLAYER (
ID INT PRIMARY KEY NOT NULL,
NAME TEXT NOT NULL
);
''')
        for p in game_mgr.player_mgr.loop_players():
            sql = f'''INSERT INTO PLAYER (ID, NAME) VALUES
({p.player_id}, "{p.player_name}");'''
            cursor.execute(sql)

# CITY        
        cursor.execute('''
CREATE TABLE CITY (
ID INT PRIMARY KEY NOT NULL,
NAME TEXT NOT NULL,
HERO_LIST INT ARRAY,

SATRAP INT,
ORDER_INCHARGE INT,
FARM_INCHARGE INT,
TRADER_INCHARGE INT,
FAX_INCHARGE INT,

FAX_RATE INT,
X FLOAT,
Y FLOAT
);
''')
        
# HERO

        cursor.execute('''
CREATE TABLE HERO (
ID INT PRIMARY KEY NOT NULL,
NAME TEXT NOT NULL,
BORN_YEAR INT,
CITY_ID INT references CITY(ID)
);
''')
        for h in game_mgr.hero_mgr.loop_heros():
            sql = f'''INSERT INTO TABLE HERO (ID,NAME) VALUES
({h.hero_id}, "{h.hero_name}");'''
            cursor.execute(sql)

        cursor.execute('''
CREATE TABLE TROOP (
ID INT PRIMARY KEY NOT NULL,
NAME TEXT NOT NULL,
CHIEF_HERO_ID INT references HERO(ID),
HERO_LIST INT ARRAY[9],
X FLOAT,
Y FLOAT
);
''')
        conn.commit()
    
    def save(self, path):
        if os.path.exists(path):
            os.remove(path)
            
        conn = sqlite3.connect(path)
        self.do_save(conn)
        
        conn.close()

    def get_cur_year(self):
        return self.start_year + int(self.play_time / (86400*365))




