import time
from socket import *
import json


port=7777
host='localhost'

def create_presence_msg(name):
    return json.dumps({"action": "presence",
            "time": time.ctime(),
            "user":{"name": name,"status": "here"}})

def get_socket(port, host):
    s=socket(AF_INET, SOCK_STREAM)
    s.connect((host,port))
    return s

if __name__=='__main__':
    s= get_socket(port, host)
    msg=create_presence_msg('Client_test')

    s.send(msg.encode('utf-8'))
    data=s.recv(10000)
    print('Server message ', data.decode('utf-8'))
    s.close()
