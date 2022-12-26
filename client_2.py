import time
from socket import *
import json
import logging
import log.client_log_config
import threading
logger=logging.getLogger('client')
from Metaclasses import ClientVerify

#port=7777
host='localhost'
from descriptor import Port
class Client(metaclass=ClientVerify):
    port = Port()

    def __init__(self, name, port_val, host_val):
        self.port=port_val
        self.host=host_val
        self.name=name
        s = socket(AF_INET, SOCK_STREAM)
        s.connect((self.host, self.port))
        self.s=s

    def create_presence_msg(self):
        return json.dumps({"action": "presence",
                "time": time.ctime(),
                "user":{"name": self.name,"status": "here"}})

    def create_msg(self,to_user, text):
        return json.dumps({"action": "msg",
                           "text":text,
                "time": time.ctime(),
                "user":{"name": self.name,"status": "here"},
                          'to_user':to_user})

    def get_client_socket(self,port, host):
        s=socket(AF_INET, SOCK_STREAM)
        s.connect((host,port))
        return s

    def send(self, msg):
        try:
            self.s.send(msg.encode('utf-8'))
            logger.debug(f'The message {msg} is sent')
        except AttributeError as e:
            logger.error(e)

    def user_communication(self):
        name=input('Please, enter your name')
        while 1:
            msg=input('Enter your message, or q for exit')
            if msg=='q':
                break
            else:
                self.send(self.create_msg(name, msg), self.s)

    def recieve(self):
        while True:
            try:
                time.sleep(2)
                data = self.s.recv(10000)
                logger.debug(f'The message {data.decode("utf-8")} is recieved ')

            except BaseException as e:
                logger.error(e)
                logger.debug(f'recieve finished')
                break

    def message_bot_sender(self):
        msg = self.create_presence_msg()
        msg_2 = self.create_msg('all', "Anybody is here?")
        msg_3 = self.create_msg('Mary', "It seems, there are nobody")
        msg_5 = self.create_presence_msg()
        msg_4 = self.create_msg('Kira', "Good bue")
        msgs = [msg,  msg_3, msg_5, msg_4]

        for msg in msgs:
            self.send(msg)
            time.sleep(5)

if __name__=='__main__':
    try:

        Mary=Client('Mary',3537, host)

        #message_bot_sender()
        thr_send= threading.Thread(target=Mary.message_bot_sender,args=(), daemon=1)
        thr_send.start()
        # recieve(s)

        thr_recieve= threading.Thread(target=Mary.recieve, args=(), daemon=1)
        thr_recieve.start()

        while True:
            time.sleep(10)
            if thr_recieve.is_alive() and thr_send.is_alive():
                continue
            break
        logger.debug(f'client finished')

    except ConnectionRefusedError as e:
        logger.error(e)
