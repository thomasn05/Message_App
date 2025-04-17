import json
from pathlib import Path
from ds_messenger import DirectMessage
import psycopg2
import os
from dotenv import load_dotenv

class DsuFileError(Exception):
    pass

class DsuProfileError(Exception):
    pass

class Profile:

    def __init__(self, dsuserver : str = None, username : str = None, password : str = None):
        self.dsuserver = dsuserver # REQUIRED
        self.username = username # REQUIRED
        self.password = password # REQUIRED
        self.friends =  {}
        self.path = f'{self.username}.dsu'

        load_dotenv()
        try:
            self.conn = psycopg2.connect(
                host= os.getenv('DB_HOST'),
                database= os.getenv('DB_NAME'),
                user= os.getenv('DB_USER'),
                password= os.getenv('DB_PASSWORD'),
                port= os.getenv('DB_PORT')
            )
            self.conn.autocommit = True
            self.cursor = self.conn.cursor()

            self.__create_tables()
            self.__add_user()
        
        except Exception as ex:
            raise DsuProfileError("Error while attempting to connect to the database.", ex)

    def __create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username VARCHAR PRIMARY KEY,
                password VARCHAR NOT NULL
            );
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS friends (
                username VARCHAR NOT NULL,
                friend VARCHAR NOT NULL,
                PriMARY KEY (username, friend)
            );
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                sender VARCHAR NOT NULL,
                recipient VARCHAR NOT NULL,
                message TEXT NOT NULL,
                timestamp TIMESTAMP
            );
        """)

    def __add_user(self):
        self.cursor.execute("""
            INSERT INTO users (username, password) VALUES (%s, %s)
            ON CONFLICT (username) DO NOTHING;
        """, (self.username, self.password))



    def add_friend(self, username : str) -> None:
        if username not in self.friends:
            self.friends[username] = []
            self.save_profile()

    def add_direct_message(self, direct_msg : DirectMessage) -> None:
        if direct_msg.sender == self.username:
            friend = direct_msg.recipient
        else:
            friend = direct_msg.sender
        self.friends[friend].append({'from': direct_msg.sender, 'to': direct_msg.recipient, 'message' : direct_msg.message, 'time' : direct_msg.timestamp})
        self.save_profile()

    def save_profile(self) -> None:
        p = Path(self.path)

        try:
            f = open(p, 'w')
            json.dump(self.__dict__, f)
            f.close()
        except Exception as ex:
            raise DsuFileError("Error while attempting to process the DSU file.", ex)

    def load_profile(self) -> bool:
        p = Path(self.path)

        if p.exists():
            f = open(p, 'r')
            obj = json.load(f)
            self.username = obj['username']
            self.password = obj['password']
            self.dsuserver = obj['dsuserver']
            self.friends = obj['friends']
            f.close()
            return 1
        return 0
