import unittest as u
from ds_protocol import extract_json
import json

class ds_protocal_test(u.TestCase):
    message = {"response": {"type": "ok", "message": "Direct message sent"}}
    msg_result = extract_json(json.dumps(message))

    messages = {"response": {"type": "ok", "messages": [{'hi' : 'Test'}]}}
    msgs_result = extract_json(json.dumps(messages))



    def test_type(self):
        result = ds_protocal_test.msg_result
        self.assertEqual(result.type, "ok")
    
    def test_direct_message(self):
        result = ds_protocal_test.msg_result
        self.assertEqual(result.message, 'Direct message sent')

    def test_request_msgs(self):
        result = ds_protocal_test.msgs_result
        self.assertEqual(result.message, [{'hi' : 'Test'}])
    

if __name__ == "__main__":
    u.main()