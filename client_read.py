import time
from socket import *
import json
import logging
import log.client_log_config
import threading
logger=logging.getLogger('client')

port=7777
host='localhost'

def create_presence_msg(name):
    return json.dumps({"action": "presence",
            "time": time.ctime(),
            "user":{"name": name,"status": "here"}})

def send(msg, s):
    try:
        s.send(msg.encode('utf-8'))
        logger.debug(f'The message {msg} is sent')
    except AttributeError as e:
        logger.error(e)

def get_client_socket(port, host):
    s=socket(AF_INET, SOCK_STREAM)
    s.connect((host,port))
    return s

def recieve(s):
    #send(create_presence_msg('Kira'), s)
    while True:
        try:
            time.sleep(2)
            data = s.recv(10000)
            logger.debug(f'The message {data.decode("utf-8")} is recieved ')

        except BaseException as e:
            logger.error(e)
            logger.debug(f'recieve finished')
            break

if __name__=='__main__':
    try:
        s= get_client_socket(port, host)
        #recieve(s)
        logger.debug(f'client-read start')
        thr_recieve= threading.Thread(target=recieve, args=(s,), daemon=1)
        thr_recieve.start()
        #
        while True:
            time.sleep(10)
            if thr_recieve.is_alive():
                continue
            break
        logger.debug(f'client-read finished')

    except ConnectionRefusedError as e:
        logger.error(e)
