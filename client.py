import time
from socket import *
import json
import logging
import log.client_log_config

logger=logging.getLogger('client')

port=7777
host='localhost'

def create_presence_msg(name):
    return json.dumps({"action": "presence",
            "time": time.ctime(),
            "user":{"name": name,"status": "here"}})

def get_client_socket(port, host):
    s=socket(AF_INET, SOCK_STREAM)
    s.connect((host,port))
    return s


def send(msg, s):
    try:
        s.send(msg.encode('utf-8'))
        logger.debug(f'The message {msg} is sent')
    except AttributeError as e:
        logger.error(e)

def recieve(s):
    try:
        data = s.recv(10000)
        logger.debug(f'The message {data.decode("utf-8")} is recieved')
        return data.decode('utf-8')
    except BaseException as e:
        logger.error(e)

if __name__=='__main__':
    try:
        s= get_client_socket(port, host)
        msg=create_presence_msg('Client_test')
        send(msg, s)
        recieve(s)
        s.close()

    except ConnectionRefusedError as e:
        logger.error(e)
