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
);''')
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
X FLOAT,Z FLOAT
);''')
        for unit in game_mgr.unit_mgr.loop_cities():
            sql = f'''INSERT INTO CITY (ID,NAME) 
VALUES (
{unit.unit_id},"{unit.unit_name}"
);'''
            cursor.execute(sql)
        conn.commit()

# HERO

        cursor.execute('''
CREATE TABLE HERO (
ID INT PRIMARY KEY NOT NULL,
NAME TEXT NOT NULL,
OWNER_PLAYER_ID INT references Player(ID),
OWNER_CITY_ID INT references CITY(ID),
BORN_YEAR INT
);''')
        for h in game_mgr.hero_mgr.loop_heros():
            sql = f'''INSERT INTO HERO (ID,NAME,OWNER_PLAYER_ID,OWNER_CITY_ID)
VALUES (
{h.hero_id},"{h.hero_name}",
{h.owner_player_id},{h.owner_city_id}
);'''
            cursor.execute(sql)
        conn.commit()

# TROOP
        cursor.execute('''
CREATE TABLE TROOP (
ID INT PRIMARY KEY NOT NULL,
NAME TEXT NOT NULL,
OWNER_CITY_ID INT references CITY(ID),
CHIEF_HERO_ID INT references HERO(ID),
HERO_LIST INT ARRAY[9],
ARMY_AMOUNT INT,
ARMY_MORAL INT,
X FLOAT,Z FLOAT
);''')
        for unit in game_mgr.unit_mgr.loop_troops():
            hero_list = ','.join(map(lambda x: str(x.hero_id), unit.hero_list))
            sql = f'''INSERT INTO TROOP
(ID,NAME,
OWNER_PLAYER_ID,OWNER_CITY_ID,
CHIEF_HERO_ID,HERO_LIST,
ARMY_AMOUNT,ARMY_MORAL,
X,Z)
VALUES (
{unit.unit_id},"{unit.unit_name}",
{unit.owner_player_id},{unit.owner_city_id},
{unit.chief_hero_id},'{hero_list}',
{unit.army_amount.get_round()},{unit.army_moral.get_round()}
{unit.get_x()},{unit.get_z()}
);'''
            cursor.execute(sql)
        conn.commit()
    
    def save(self, path):
        if os.path.exists(path):
            os.remove(path)
            
        conn = sqlite3.connect(path)
        self.do_save(conn)
        
        conn.close()

    def get_cur_year(self):
        return self.start_year + int(self.play_time / (86400*365))




