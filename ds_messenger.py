import socket as s
from time import time
import ds_protocol as dp
import json
import datetime

class DirectMessage:
    def __init__(self, recipient : str, sender : str,  message : str, timestamp : datetime):
        self.recipient = recipient
        self.sender = sender
        self.message = message
        self.timestamp = timestamp
        
class DirectMessenger:
    def __init__(self, dsuserver : str = None, username : str = None, password : str = None):
        self.dsuserver, self.username, self.password= dsuserver, username, password
        self.port = 3021
        self.token = 0
        self.error = 0
        self.__join()

    def __join(self) -> str: #Get token from joining
        join_json = {"join": {"username" : self.username, "password" : self.password, "token" : ""}}#Data to be send

        response = self.__server_send(join_json)
        
        if not response: #unable to connect to serber
            self.error = 'Cannot connect to server'
            return 0

        if response.type == 'ok': #Get token if successful otherwise print error msg
            self.token = response.token
            return
        
        elif response.type == 'error':
            self.error = response.message
            return
            
    def __server_send(self, json_data : dict) -> dp.DataTuple:
        socket = s.socket(s.AF_INET, s.SOCK_STREAM) #Create socket
        try:
            socket.connect((self.dsuserver, self.port))
        except:
            return 0
        
        #Getting data in json string format
        json_data1 = json.dumps(json_data)
        socket.send(json_data1.encode('utf-8')) #Sending to server and recieving server response
        response = socket.recv(2048).decode('utf-8')
        socket.close()

        response = dp.extract_json(response) #converting to dict
        return response

    def __convert_DirectMessage(self, msgs : list[dict]) -> list:
        direct_msgs = []
        for msg in msgs: 
            direct_msg = DirectMessage(self.username, msg['from'] , msg['message'], msg['timestamp'])
            direct_msgs.append(direct_msg)
        
        return direct_msgs

    def send(self, message:str, recipient:str) -> bool:
        # must return true if message successfully sent, false if send failed.
        curr_time = time()
        json_msg = {"token" : self.token, "directmessage": {"entry" : message,"recipient": recipient, "timestamp": curr_time}}
        msg_obj = DirectMessage(recipient, self.username, message, curr_time)

        response = self.__server_send(json_msg)
        
        if not response: return 0

        return response.type == 'ok'

    def retrieve_new(self) -> list:
        # must return a list of DirectMessage objects containing all new messages
        new_msg_json = {"token" : self.token, "directmessage" : "new"}
        
        msgs = self.__server_send(new_msg_json).message

        msgs = self.__convert_DirectMessage(msgs)

        return msgs
    
    def retrieve_all(self) -> list:
        # must return a list of DirectMessage objects containing all messages
        all_msg_json = {"token" : self.token, "directmessage" : "all"}
        
        msgs = self.__server_send(all_msg_json).message

        msgs = self.__convert_DirectMessage(msgs)

        return msgs