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

def create_msg(name,to_user, text):
    return json.dumps({"action": "msg",
                       "text":text,
            "time": time.ctime(),
            "user":{"name": name,"status": "here"},
                      'to_user':to_user})

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

def user_communication(s):
    name=input('Please, enter your name')
    while 1:
        msg=input('Enter your message, or q for exit')
        if msg=='q':
            break
        else:
            send(create_msg(name, msg), s)

def recieve(s):
    while True:
        try:
            time.sleep(2)
            data = s.recv(10000)
            logger.debug(f'The message {data.decode("utf-8")} is recieved ')

        except BaseException as e:
            logger.error(e)
            logger.debug(f'recieve finished')
            break


def message_bot_sender():
    msg = create_presence_msg('Mary')
    msg_2 = create_msg('Mary','all', "Anybody is here?")
    msg_3 = create_msg('Mary','Mary', "It seems, there are nobody")
    msg_5 = create_presence_msg('Kira')
    msg_4 = create_msg('Mary','Kira', "Good bue")
    msgs = [msg,  msg_3, msg_5, msg_4]

    for msg in msgs:
        send(msg, s)
        time.sleep(5)

if __name__=='__main__':
    try:
        s= get_client_socket(port, host)

        #message_bot_sender()
        thr_send= threading.Thread(target=message_bot_sender,args=(), daemon=1)
        thr_send.start()
        # recieve(s)

        thr_recieve= threading.Thread(target=recieve, args=(s,), daemon=1)
        thr_recieve.start()

        while True:
            time.sleep(10)
            if thr_recieve.is_alive() and thr_send.is_alive():
                continue
            break
        logger.debug(f'client finished')

    except ConnectionRefusedError as e:
        logger.error(e)
