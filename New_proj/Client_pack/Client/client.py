import time
from socket import *
import json
import logging
import log.client_log_config
import threading
logger=logging.getLogger('client')
from PyQt5 import QtCore, QtGui, QtWidgets
from Metaclasses import ClientVerify
from descriptor import Port

from Client_database_creation import Contact, Msg_history, Contact_list
from sqlalchemy import create_engine, desc, or_, and_
from sqlalchemy.orm import sessionmaker
import hmac
import os
import hashlib


port=7777
host='127.0.0.1'
socket_lock = threading.Lock()

engine = create_engine('sqlite:///client_base.db3', connect_args={"check_same_thread":False})
Session = sessionmaker(bind=engine)
session = Session()

class Client():
    def __init__(self, name, port_val, host_val, password):
        """Документация метода ``__init__``"""
        self.port=port_val
        self.host=host_val
        self.name=name
        self.password=password
        self.s = self.get_client_socket(self.port, self.host)
        self.recv_message= ''

    def db_contact_list(self):
        result = []
        contact_list = session.query(Contact_list).all()
        for line in contact_list:
            contact = session.query(Contact).filter_by(id=line.contact_id).first()
            result.append(contact.name)
        return result

    def client_history(self, chat_with):
        contact = session.query(Contact).filter_by(name=chat_with).first()
        msgs = session.query(Msg_history).filter(and_(
                                                      or_(Msg_history.from_==self.name, Msg_history.from_==contact.name),
                                                      or_(Msg_history.to_==contact.name, Msg_history.to_==self.name))).order_by(desc(Msg_history.id)).limit(6)
        msg_list=[]
        msg_history=''
        for msg in msgs:
            msg= msg.msg +'\n'+str(msg.time.replace(microsecond=0))+ ' from '+msg.from_+'\n\n'
            msg_list.append(msg)
        for msg in msg_list[::-1]:
            msg_history+=msg
            #self.chat.setText(self.chat.toPlainText() + msg)
        return msg_history

    def recieve(self):
        """Функция получения сообщений"""
        while True:
            try:
                data = self.s.recv(10000)
                #logger.debug(f'The message {data.decode("utf-8")} is recieved ')
                print(data.decode("utf-8"))
                data = data.decode("utf-8")
                json_data = json.loads(data)
                if json_data.get('action'):
                    self.recv_message=json_data
            except BaseException as e:
                logger.error(e)
                logger.debug(f'recieve finished')
                break

    def create_identificate_msg(self):
        """Формирование сообщения с логином и паролем"""
        return json.dumps({"action": "identify",'name': self.name, 'password': self.password})

    def create_presence_msg(self):
        """Формирование presence сообщение"""
        return json.dumps({"action": "presence",
                "time": time.ctime(),
                "user":{"name": self.name,"status": "here"}})

    def create_exit_msg(self):
        """Формирование сообщения о выходе"""
        return json.dumps({"action": "exit",
                           "time": time.ctime(),
                           "user": self.name})

    def create_msg(self,to_user, text):
        """Формирование сообщения"""
        return json.dumps({"action": "msg",
                           "text":text,
                "time": time.ctime(),
                "user":{"name": self.name,"status": "here"},
                          'to_user':to_user})

    def get_client_socket(self,port, host):
        """Установка соединения"""
        s=socket(AF_INET, SOCK_STREAM)
        s.connect((host,port))
        return s

    def send(self, msg):
        """Функция отправки запросов и сообщений"""
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

    def user_communication(self):

        while 1:
            user= input('To user - u, to all -a, or q for exit ')
            if user=='q':
                exit_msg=self.create_exit_msg()
                self.send(exit_msg)
                break
            elif user == 'u':
            #text=input('Enter your message ')
                msg_2 = self.create_msg('Mary', 'hey')
                self.send(msg_2)
            elif user == 'a':
                msg_3 = self.create_msg('all', 'hello everybody')
                self.send(msg_3)
            elif user == 'add':
                msg_4 = self.add_contact('Mary')
                self.send(msg_4)
            elif user == 'get':
                msg_5 = self.get_contacts()
                self.send(msg_5)
            elif user == 'del':
                msg_6 = self.del_contact('Mary')
                self.send(msg_6)

    def client_authenticate(self):
        """Аутентификация клиента"""
        message = self.s.recv(32)
        hash = hmac.new(b'our_secret_key', message, digestmod=hashlib.sha256)
        digest = hash.digest()
        self.s.send(digest)

    def get_contacts(self):
        """Запрос списка контактов"""
        return json.dumps({"action": "get_contacts", "time": time.ctime(), "user_login": self.name})

    def add_contact(self, nickname):
        """Запрос на добавление контакта"""
        return json.dumps({"action": "add_contact", "user_id": nickname, "time": time.ctime(), "user_login": self.name})

    def del_contact(self, nickname):
        """Запрос на удаление контакта"""
        return json.dumps({"action": "del_contact", "user_id": nickname, "time": time.ctime(), "user_login": self.name})

    def contact_in_database(self, nickname, command):
        """Добавление контакта в базу данных клиента"""
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

    def add_msg_in_history(self, msg, send=True):
        """Добаление сообщения в базу данных клиента"""
        with socket_lock:
            if send:
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
                    logger.debug('Message in database')
                except:
                    session.rollback()
                    logger.debug('Error, can`t add message into database')
            else:
                try:
                    client=session.query(Contact).filter_by(name=msg['to_user']).first()
                    if client is None:
                        client = Contact(self.name)
                        session.add(client)
                    contact = session.query(Contact).filter_by(name=msg['user']['name']).first()
                    if contact is None:
                        contact = Contact(msg['to_user'])
                        session.add(contact)
                    msg = Msg_history(contact.name, client.name, msg['text'])
                    session.add(msg)
                    session.commit()
                    logger.debug('Message in database')
                except:
                    session.rollback()
                    logger.debug('Error, can`t add message into database')

if __name__=='__main__':
    try:
        import sys

        logger.debug(f'client-read start')

        Mary = Client('Thomas', 7777, host, '1234')

        Mary.send(Mary.create_identificate_msg())

        Mary.send(Mary.create_presence_msg())

        thr_recieve = threading.Thread(target=Mary.recieve, args=(), daemon=1)
        thr_recieve.start()

        thr_send = threading.Thread(target=Mary.user_communication(), args=(), daemon=1)
        thr_send.start()


        while True:
            time.sleep(10)
            if thr_send.is_alive():
                continue
            break

        logger.debug(f'client-read finished')

    except ConnectionRefusedError as e:
        logger.error(e)
