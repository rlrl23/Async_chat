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
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker, query

class Client(metaclass=ClientVerify):
    port = Port()

    def __init__(self, name, port_val, host_val):
        self.port=port_val
        self.host=host_val
        self.name=name
        s = socket(AF_INET, SOCK_STREAM)
        s.connect((self.host, self.port))
        self.s=s

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
               self.add_msg_in_history(msg)
            elif msg['action'] == "add_contact":
                self.contact_in_database(msg['user_id'], 'add')
            elif msg['action'] == "del_contact":
                self.contact_in_database(msg['user_id'], 'del')
            elif msg['action'] == "get_contacts":
                self.contact_in_database(msg['user_login'], 'get')

        except AttributeError as e:
            logger.error(e)

    def contact_in_database(self, nickname, command):
        engine = create_engine('sqlite:///client_base.db3')
        Session = sessionmaker(bind=engine)
        session = Session()
        try:

            client=session.query(Contact).filter_by(name=self.name).first()
            contact = session.query(Contact).filter_by(name=nickname).first()
            if contact is None:
                contact = Contact(nickname)
                session.add(contact)
                session.commit()
            if client is None:
                client = Contact(self.name)
                session.add(client)
                session.commit()
            if command == 'add':
                contact_list = session.query(Contact_list).filter_by(contact_id=contact.id, host_id=client.id).first()

                if contact_list is None:
                    contact_list = Contact_list(client.id, contact.id)
                    session.add(contact_list)
                    session.commit()
                else: logger.debug(f'{nickname} уже в списке контактов')
            elif command=='del':
                try:
                    contact_list = session.query(Contact_list).filter_by(contact_id=contact.id,
                                                                         host_id=client.id).first()
                    session.delete(contact_list)
                    session.commit()
                    logger.debug(f'{nickname} удален из списка контактов')
                except:
                    logger.debug(f'{nickname} ошибка удаления')
            elif command=='get':
                result=[]
                contact_list = session.query(Contact_list).all()
                for line in contact_list:
                    contact=session.query(Contact).filter_by(id=line.contact_id).first()
                    result.append(contact.name)
                logger.debug(f'Cписок контактов: {result} ')
        except:
            session.rollback()
            logger.debug('Error, can`t add/del/get contact ')

    def add_msg_in_history(self, msg):
        engine = create_engine('sqlite:///client_base.db3')
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            client=session.query(Contact).filter_by(name=self.name).first()
            if client is None:
                client = Contact(self.name)
                session.add(client)
            contact = session.query(Contact).filter_by(name=msg['to_user']).first()
            if contact is None:
                contact = Contact(msg['to_user'])
                session.add(contact)
            msg = Msg_history(client.name, contact.name, msg['text'])
            session.add(msg)
            session.commit()
        except:
            session.rollback()
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
        while True:
            try:
                time.sleep(2)
                data = self.s.recv(10000)
                logger.debug(f'The message {data.decode("utf-8")} is recieved ')
                data= data.decode("utf-8")
                data = data.replace('}{', '};{')
                msgs_in_data = data.split(';')
                for msg in msgs_in_data:
                    json_data = json.loads(msg)
                    if json_data.get('action'):
                        self.add_msg_in_history(json_data)
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
        msgs = [msg, msg_5, msg_9, msg_7, msg_5, msg_4]

        for msg in msgs:
            self.send(msg)
            time.sleep(5)

if __name__=='__main__':
    try:

        Mary=Client('Mary',7777, host)



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
