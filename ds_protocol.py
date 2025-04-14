import json
from collections import namedtuple

# Namedtuple to hold the values retrieved from json messages.
# TODO: update this named tuple to use DSP protocol keys
DataTuple = namedtuple('DataTuple', ['type','message', 'token'])

def extract_json(json_msg:str) -> DataTuple:
	'''
	Call the json.loads function on a json string and convert it to a DataTuple object
	'''
	token = ''
	try:
		json_obj = json.loads(json_msg)
		response = json_obj['response']
		msg = list(response.keys())[1]
		type, message = response['type'], response[msg]
		if 'token' in response.keys():
			token = response['token']
	except json.JSONDecodeError:
		print("Json cannot be decoded.")

	return DataTuple(type, message, token)