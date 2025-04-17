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
                timestamp REAL NOT NULL
            );
        """)

    def __add_user(self):
        self.cursor.execute("""
            INSERT INTO users (username, password) VALUES (%s, %s)
            ON CONFLICT (username) DO NOTHING;
        """, (self.username, self.password))

    def load_profile(self):
        self.__add_user()

        self.load_friends()

        self.load_messages()

    def load_friends(self):
        self.cursor.execute("""
            SELECT friend FROM friends WHERE username = %s;
        """, (self.username,))
        friends = self.cursor.fetchall()
        for friend in friends:
            self.friends[friend[0]] = []
    
    def load_messages(self):
        self.cursor.execute("""
            SELECT sender, recipient, message, timestamp FROM messages WHERE sender = %s OR recipient = %s;
            """, (self.username, self.username))
        for sender, recipient, message, timestamp in self.cursor.fetchall():
            friend = recipient if sender == self.username else sender
            direct_msg = DirectMessage(recipient, sender, message, timestamp)
            self.friends[friend].append(direct_msg)

    def add_friend(self, username : str) -> None:
        if username not in self.friends:
            self.friends[username] = []

        self.cursor.execute("""
            INSERT INTO friends (username, friend) VALUES (%s, %s)
            ON CONFLICT (username, friend) DO NOTHING;
        """, (self.username, username))

    def add_direct_message(self, direct_msg : DirectMessage) -> None:
        friend = direct_msg.recipient if direct_msg.sender == self.username else direct_msg.sender
        self.friends[friend].append(DirectMessage(direct_msg.recipient, direct_msg.sender, direct_msg.message, direct_msg.timestamp))

        self.cursor.execute("""
            INSERT INTO messages (sender, recipient, message, timestamp) VALUES (%s, %s, %s, %s);
        """, (direct_msg.sender, direct_msg.recipient, direct_msg.message, direct_msg.timestamp))
            