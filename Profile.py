from ds_messenger import DirectMessage
import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv


"""
DsuFileError is a custom exception handler that you should catch in your own code. It
is raised when attempting to load or save Profile objects to file the system.
"""
class DsuFileError(Exception):
    pass

"""
DsuProfileError is a custom exception handler that you should catch in your own code. It
is raised when attempting to deserialize a dsu file to a Profile object.
"""
class DsuProfileError(Exception):
    pass

class Profile:
    def __init__(self, dsuserver : str = None, username : str = None, password : str = None):
        self.dsuserver = dsuserver # REQUIRED
        self.username = username # REQUIRED
        self.password = password # REQUIRED
        
        load_dotenv()
        try:
            self.conn = psycopg2.connect(
                dbname=os.getenv('DB_NAME'), 
                user=os.getenv('DB_USER'), 
                password=os.getenv('DB_PASSWORD'), 
                host=os.getenv('DB_HOST'), 
                port=os.getenv('DB_PORT'))
            self.conn.autocommit = True
            self.cursor = self.conn.cursor()
            self.__create_tables()
            self.__add_user()
        except Exception as e:
            raise DsuFileError("Error while attempting to connect to the database.", e)

    def __create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username VARCHAR PRIMARY KEY,
            password VARCHAR NOT NULL
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS friends (
            username VARCHAR,
            friend VARCHAR,
            PRIMARY KEY (username, friend)
        );
""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            sender VARCHAR,
            recipient VARCHAR,
            message TEXT,
            timestamp TIMESTAMP
        );
        """)

    def add_friend(self, friend : str) -> None:
        self.cursor.execute("""
        INSERT INTO friends (username, friend) 
        VALUES (%s, %s) 
        ON CONFLICT DO NOTHING""", (self.username, friend))

    def add_direct_message(self, direct_msg : DirectMessage) -> None:
        self.cursor.execute("""
        INSERT INTO messages (sender, recipient, message, timestamp)
        VALUES (%s, %s, %s, %s)""", (direct_msg.sender, direct_msg.recipient, direct_msg.message, datetime.fromtimestamp(direct_msg.timestamp)))

    def __add_user(self) -> None:
        self.cursor.execute("""
        INSERT INTO users (username, password)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING""", (self.username, self.password))

    def get_friends(self) -> tuple:
        self.cursor.execute("""
        SELECT friend FROM friends WHERE username = %s""", (self.username,))
        return self.cursor.fetchall()
    
    def get_messages(self, friend: str) -> list[dict]:
        self.cursor.execute("""
        SELECT sender, recipient, message, timestamp
        FROM messages
        WHERE (sender = %s AND recipient = %s)
        OR (sender = %s AND recipient = %s)
        ORDER BY timestamp;
        """, (self.username, friend, friend, self.username))
        return [
            DirectMessage(
                sender=msg[0],
                recipient=msg[1],
                message=msg[2],
                timestamp=msg[3]
            )
            for msg in self.cursor.fetchall()
        ]

