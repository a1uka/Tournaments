import json
import requests
import sqlite3
import time
from datetime import datetime, timezone

''' сlass api_key
* Занимается хранением и отвечает за удобный доступ к каждому конкретному api ключу
'''

req_link = "https://r5-crossplay.r5prod.stryder.respawn.com/privatematch/?token="

class api_key:
    def __init__(self, s_stats_token, s_adm_token, s_plr_token, s_time_start, s_time_exp):
        self.stats_token = s_stats_token
        self.adm_token = s_adm_token
        self.plr_token = s_plr_token
        self.time_start = float(s_time_start)
        self.time_exp = float(s_time_exp)
        self.matches = {}
        self.active = True
        
    
    def get_desc(self):
        return f"Admin - {self.adm_token}, player - {self.plr_token}, time_exp - {self.time_exp}"
    
    def get_stats_token(self):
        return self.stats_token
    
    def request_token(self):
        timestamp = time.time()
        if(timestamp >= self.time_start and timestamp <= self.time_exp):
            resp = requests.get(req_link + self.stats_token)
            return resp
        else:
            self.active = False
            return "Inactive"
        
    
    def get_matches(self):
        matches_json = self.request_token().json()
        if(matches_json != "Inactive"):
            self.matches = matches_json
        return self.matches

        
    
 # Чтобы не хранить в каждом классе одно и то же

''' class db_updater
* Отвечает за хранение всех api_key, их обновление (например, если новый матч закончился)
* Отвечает за добавление результатов в db
* При начале работы программы импортирует api_keys из db
* Предоставляет доступ к добавлению в db новых api_keys
* Не запрашивает данные по api_keys с истекшим сроком годности
'''
class db_handler:
    def __init__(self):
        self.db = sqlite3.connect("matches.db")
        self.cursor = self.db.cursor()
        self.cursor.execute("""
    CREATE TABLE IF NOT EXISTS api_keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stats_token TEXT NOT NULL,
        admin_code TEXT NOT NULL,
        player_code TEXT NOT NULL,
        time_start TIMESTAMP NOT NULL,
        time_expires TIMESTAMP NOT NULL,
        active INTEGER CHECK (active IN (0, 1))
    )
    """)
    
    def get_tokens(self):
        self.cursor.execute("SELECT * FROM api_keys")
        return self.cursor.fetchall()


    def add_token(self, token: api_key):
        token_tuple = (token.stats_token, token.adm_code, token.plr_code, token.time_start, token.time_exp, token.active)
        self.cursor.execute("""
        INSERT INTO api_keys (stats_token, admin_code, player_code, time_start, time_expires, active) VALUES (?, ?, ?, ?, ?, ?)
        """, token_tuple)
        self.cursor.execute("""""")

    
        

def to_timestamp(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    dt = dt.replace(tzinfo=timezone.utc) # Указываем, что время в UTC
    return dt.timestamp()

start_str = "2026-01-29 08:00:00"
end_str = "2026-05-31 07:00:00"
start_timestamp = to_timestamp(start_str)
end_timestamp = to_timestamp(end_str)
a = api_key("8398be9b-5004ef1f4e527c2c390dc9", 	"ab01cf10",	"pe4afb4b", start_timestamp, end_timestamp)
print(a.get_matches()['matches'][3]['player_results'][0].keys())
