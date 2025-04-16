import json
from pathlib import Path
from ds_messenger import DirectMessage
import psycopg2
import os
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
        except Exception as e:
            raise DsuFileError("Error while attempting to connect to the database.", e)


    "add_friend will add a friend to friends list if they are not already in it"

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

    """

    save_profile accepts an existing dsu file to save the current instance of Profile 
    to the file system.

    Example usage:

    profile = Profile()
    profile.save_profile('/path/to/file.dsu')

    Raises DsuFileError

    """
    def save_profile(self) -> None:
        p = Path(self.path)

        try:
            f = open(p, 'w')
            json.dump(self.__dict__, f)
            f.close()
        except Exception as ex:
            raise DsuFileError("Error while attempting to process the DSU file.", ex)

    """

    load_profile will populate the current instance of Profile with data stored in a 
    DSU file.

    Example usage: 

    profile = Profile()
    profile.load_profile('/path/to/file.dsu')

    Raises DsuProfileError, DsuFileError

    """
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
