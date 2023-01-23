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
from Client_database_creation import Contact, Msg_history, Contact_list
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

socket_lock = threading.Lock()

class Client(threading.Thread ,metaclass=ClientVerify):
    port = Port()

    def __init__(self, name, port_val, host_val):
        threading.Thread.__init__(self)
        self.port=port_val
        self.host=host_val
        self.name=name
        s = socket(AF_INET, SOCK_STREAM)
        s.connect((self.host, self.port))
        self.s=s
        engine = create_engine('sqlite:///client_base.db3')
        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.got_message=False


    def get_contacts(self):
        return json.dumps({"action": "get_contacts","time": time.ctime(),"user_login": self.name})

    def add_contact(self, nickname):
        return json.dumps({"action": "add_contact","user_id": nickname,"time": time.ctime(),"user_login": self.name})

    def del_contact(self, nickname):
        return json.dumps({"action": "del_contact","user_id": nickname,"time": time.ctime(),"user_login": self.name})

    def create_presence_msg(self):
        return json.dumps({"action": "presence",
                "time": time.ctime(),
                "user":{"name": self.name,"status": "here"}})

    def create_exit_msg(self):
        return json.dumps({"action": "exit",
                           "time": time.ctime(),
                           "user": {"name": self.name, "status": "here"}})

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
            msg= json.loads(msg)
            if msg['action']=="msg":
               self.add_msg_in_history(msg, True)
            elif msg['action'] == "add_contact":
                self.contact_in_database(msg['user_id'], 'add')
            elif msg['action'] == "del_contact":
                self.contact_in_database(msg['user_id'], 'del')
            elif msg['action'] == "get_contacts":
                self.contact_in_database(msg['user_login'], 'get')

        except AttributeError as e:
            logger.error(e)

    def contact_in_database(self, nickname, command):

        try:
            client=self.session.query(Contact).filter_by(name=self.name).first()
            contact = self.session.query(Contact).filter_by(name=nickname).first()
            if contact is None:
                contact = Contact(nickname)
                self.session.add(contact)
                self.session.commit()
            if client is None:
                client = Contact(self.name)
                self.session.add(client)
                self.session.commit()
            if command == 'add':
                contact_list = self.session.query(Contact_list).filter_by(contact_id=contact.id, host_id=client.id).first()

                if contact_list is None:
                    contact_list = Contact_list(client.id, contact.id)
                    self.session.add(contact_list)
                    self.session.commit()
                else: logger.debug(f'{nickname} уже в списке контактов')
            elif command=='del':
                try:
                    contact_list = self.session.query(Contact_list).filter_by(contact_id=contact.id,
                                                                         host_id=client.id).first()
                    self.session.delete(contact_list)
                    self.session.commit()
                    logger.debug(f'{nickname} удален из списка контактов')
                except:
                    logger.debug(f'{nickname} ошибка удаления')
            elif command=='get':
                result=[]
                contact_list = self.session.query(Contact_list).all()
                for line in contact_list:
                    contact=self.session.query(Contact).filter_by(id=line.contact_id).first()
                    result.append(contact.name)
                logger.debug(f'Cписок контактов: {result} ')
        except:
            self.session.rollback()
            logger.debug('Error, can`t add/del/get contact ')

    def add_msg_in_history(self, msg, send=True):
        with socket_lock:
            if send:
                try:
                    client=self.session.query(Contact).filter_by(name=self.name).first()
                    if client is None:
                        client = Contact(self.name)
                        self.session.add(client)
                    contact = self.session.query(Contact).filter_by(name=msg['to_user']).first()
                    if contact is None:
                        contact = Contact(msg['to_user'])
                        self.session.add(contact)
                    msg = Msg_history(client.name, contact.name, msg['text'])
                    self.session.add(msg)
                    self.session.commit()
                except:
                    self.session.rollback()
                    logger.debug('Error, can`t add message into database')
            else:
                try:
                    client=self.session.query(Contact).filter_by(name=msg['to_user']).first()
                    if client is None:
                        client = Contact(self.name)
                        self.session.add(client)
                    contact = self.session.query(Contact).filter_by(name=msg['user']['name']).first()
                    if contact is None:
                        contact = Contact(msg['to_user'])
                        self.session.add(contact)
                    msg = Msg_history(contact.name, client.name, msg['text'])
                    self.session.add(msg)
                    self.session.commit()

                    self.got_message = True
                except:
                    self.session.rollback()
                    logger.debug('Error, can`t add message into database')

    def user_communication(self):
        name=input('Please, enter your name')
        while 1:
            msg=input('Enter your message, or q for exit')
            if msg=='q':
                break
            else:
                self.send(self.create_msg(name, msg), self.s)

    def recieve(self):
        time.sleep(2)
        while True:
            try:
                data = self.s.recv(10000)
                logger.debug(f'The message {data.decode("utf-8")} is recieved ')
                data= data.decode("utf-8")
                data = data.replace('}{', '};{')
                msgs_in_data = data.split(';')
                for msg in msgs_in_data:
                    json_data = json.loads(msg)
                    if json_data.get('action'):
                        self.add_msg_in_history(json_data, False)
            except BaseException as e:
                logger.error(e)
                logger.debug(f'recieve finished')
                break

    def message_bot_sender(self):

        msg = self.create_presence_msg()
        msg_2 = self.create_msg('all', "Anybody is here?")
        msg_3 = self.create_msg('Thomas', "It seems, there are nobody")
        msg_5 = self.create_presence_msg()
        msg_4 = self.create_msg('all', "Good bue")
        msg_5= self.get_contacts()
        msg_6=self.add_contact('Thomas')
        msg_7=self.del_contact('Bill')
        msg_8=self.add_contact('Bill')
        msg_9 = self.add_contact('Bob')
        msgs = [msg, msg_2, msg_5, msg_4]

        for msg in msgs:
            self.send(msg)
            time.sleep(5)

if __name__=='__main__':
    try:

        Mary=Client('Mary',7777, host)

        Mary.message_bot_sender()

        Mary.setDaemon(True)
        Mary.start()

        thr_recieve = threading.Thread(target=Mary.recieve, args=(), daemon=1)
        thr_recieve.start()

        print('ok')

        while True:
            if thr_recieve.is_alive():
                continue


        #message_bot_sender()
        # thr_send= threading.Thread(target=Mary.message_bot_sender,args=(), daemon=1)
        # thr_send.start()
        #
        # # recieve(s)
        #
        # thr_recieve= threading.Thread(target=Mary.recieve, args=(), daemon=1)
        # thr_recieve.start()
        #
        # while True:
        #     time.sleep(10)
        #     if thr_recieve.is_alive() and thr_send.is_alive():
        #         continue
        #     Mary.send(Mary.create_exit_msg())
        #     break
        # logger.debug(f'client finished')

    except ConnectionRefusedError as e:
        logger.error(e)
