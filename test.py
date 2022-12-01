import unittest
import json
import time
from server import create_response_msg, get_socket
from client import create_presence_msg, get_client_socket

class TestServerClient(unittest.TestCase):
    def test_get_serv_socket(self):
        self.assertTrue(get_socket(7777))

    def test_create_200_response(self):
        data= (json.dumps({"action": "presence",
            "time": '',
            "user":{"name": 'name',"status": "here"}})).encode('utf-8')
        self.assertEqual(json.loads(create_response_msg(data)),{"response": 200, "alert": "ok"})
    def test_create_400_response(self):
        data= (' ').encode('utf-8')
        self.assertEqual(json.loads(create_response_msg(data)),{"response": 400, "alert": "error"})
    def test_create_presence(self):
        self.assertEqual(json.loads(create_presence_msg('')), {"action": "presence","time": time.ctime(),"user":{"name": "","status": "here"}})
    def test_get_client_socket(self):
        s= get_socket(7777)
        time.sleep(20)
        self.assertTrue(get_client_socket(7777, 'localhost'))
        client, addr = s.accept()
        client.close()