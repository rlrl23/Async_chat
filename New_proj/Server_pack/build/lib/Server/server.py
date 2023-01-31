from socket import *
import json
import logging
import time
import log.server_log_config
from functools import wraps
import inspect
import select
from Metaclasses import ServerVerify
from descriptor import Port
logger=logging.getLogger('server')
from sqlalchemy import create_engine, and_
from Database_creation import Client_history, Client_table, Client_list, Client_password
from sqlalchemy.orm import sessionmaker, query, scoped_session
import threading
import hmac
import os
import hashlib

port=7777
host='localhost'
database= 'sqlite:///server_base.db3'
ip=''

class Server(metaclass=ServerVerify):
    def __init__(self, port, ip, database):
        self.port = port
        self.ip = ip
        self.database = database

        engine = create_engine(self.database, connect_args={"check_same_thread":False})
        Session = sessionmaker(autocommit= False, autoflush=False, bind=engine)
        self.session = Session()

        self.clients = []
        self.client_host_port = {}
        self.names = {}
        self.msgs={}

    def run(self):
        """Функция запуска сервера."""
        socket = self.get_socket()
        self.r = []
        self.w = []
        while 1:
            try:
                client, addr = socket.accept()
                logger.debug(f'Запрос получен от {str(addr)}')

                self.client_host_port[client] = addr
                self.clients.append(client)

                try:
                    if self.clients:
                        self.r, self.w, e = select.select(self.clients, self.clients, [], 10)

                except OSError as err:
                    logger.error(f'Ошибка работы с сокетами: {err.errno}')
                if self.r:
                    for c_with_msg in self.r:
                        try:
                            self.thr_recieve=threading.Thread(target=self.recieve, args=(c_with_msg,), daemon=1)
                            self.thr_recieve.start()

                        except:
                            self.r.remove(c_with_msg)

            except OSError as e:
                pass
                #logger.error(e)

    def server_authenticate(self, connection):
        """Аутентификация клиента"""
        message = os.urandom(32)
        connection.send(message)
        hash = hmac.new(b'our_secret_key', message, digestmod=hashlib.sha256)
        digest = hash.digest()
        response = connection.recv(len(digest))
        if hmac.compare_digest(digest, response) == False:
            connection.close()

    def identify(self, client, name_password):
        """Идентификация клиента"""
        client_password = self.session.query(Client_password).filter_by(socket=name_password['name']).first()

        if client_password is None:
            solt = os.urandom(16)
            hash_password = hashlib.pbkdf2_hmac('sha256', name_password['password'].encode(), solt, 100000)
            client_password = Client_password(solt + hash_password, name_password['name'])
            self.session.add(client_password)
            self.session.commit()
            logger.debug('Client is registered')
            return True
        else:
            solt = client_password.password[:16]
            hash_password = hashlib.pbkdf2_hmac('sha256', name_password['password'].encode(), solt, 100000)
            if hash_password != client_password.password[16:]:
                logger.debug('Идентификация не пройдена')
                self.clients.remove(client)
                return False
            else:
                return True

    def log(func):
        @wraps(func)
        def call(*args, **kwargs):
            main_func = inspect.stack()[-2][-3]
            logger.debug(f'Func {func.__name__}{args, kwargs} was called from {main_func}')
            return func(*args, **kwargs)

        return call

    @log
    def send_to_all(self):
        """Отправка сообщения всем"""
        try:
            group_messages = self.msgs['all']
            if type(group_messages) == list:
                for msg in group_messages:
                    for c in self.w:
                        try:
                            c.send(msg.encode('utf-8'))
                            logger.debug(f'{msg} is sent')
                        except:
                            c.close()
                            self.w.remove(c)
                            logger.error('Клиент отключился')
            else:
                for c in self.w:
                    try:
                        c.send(group_messages.encode('utf-8'))
                        logger.debug(f'{group_messages} is sent')
                    except:
                        c.close()
                        self.w.remove(c)
                        logger.error('Клиент отключился')

            self.msgs.pop('all')

        except BaseException as e:
            logger.error(e)

    def send_to_user(self):
        """Отправка сообщения клиенту"""
        try:
            for key in self.msgs:
                if key in self.names:
                    msg = self.msgs[key]
                    client = self.names[key]
                    if type(msg) == list:
                        for m in msg:
                            client.send(m.encode('utf-8'))
                            logger.debug(f'{m} is sent')
                    else:
                        client.send(msg.encode('utf-8'))
                        logger.debug(f'{msg} is sent')

                else:
                    logger.error('Такого пользователя в чате нет')
            self.msgs.pop(key)
        except BaseException as e:
            logger.error(e)

    def recieve(self, client):
        """Получение сообщений, разбор, перенаправление"""
        exit=True
        time.sleep(2)
        while exit:
            try:
                data = client.recv(100000)

                data = data.decode('utf-8')
                data = data.replace('}{', '};{')
                msgs_in_data = data.split(';')
                for msg in msgs_in_data:
                    json_data = json.loads(msg)

                    if json_data['action'] == 'identify':
                        logger.debug('got password')
                        if self.identify(client, json_data):
                            self.names[json_data['name']] = client

                    elif json_data['action'] == 'presence' and json_data['user']['name'] in self.names:
                        logger.debug('got presence')

                        self.client_login(json_data['user']['name'], ip=str(self.client_host_port[client]))

                        self.msgs[json_data['user']['name']] = [json.dumps({'response': 200, 'alert': 'ok'})]
                        self.send_to_user()

                    elif json_data['action'] == 'exit':
                        client_name=json_data['user']
                        self.client_logout(client_name)
                        self.names.pop(client_name)
                        self.clients.remove(client)
                        logger.debug(f'{client_name} exit')
                        exit=False

                    elif json_data['action'] == 'msg':
                        logger.debug('got message')

                        self.msgs[json_data['to_user']] = json.dumps(json_data)
                        if 'all' in self.msgs:
                            self.send_to_all()
                        else: self.send_to_user()

                    elif json_data['action'] == 'get_contacts' and json_data['user_login'] in self.names:
                        logger.debug('got get contacts')
                        contact_list = self.client_contact_list(json_data['user_login'])
                        answer = json.dumps({'response': 202, 'alert': contact_list})
                        self.msgs[json_data['user_login']] = answer
                        self.send_to_user()

                    elif json_data['action'] == 'add_contact':
                        logger.debug('got add contact')
                        self.msgs[json_data['user_login']] = self.add_contact(json_data['user_id'],
                                                                             json_data['user_login'])
                        self.send_to_user()

                    elif json_data['action'] == 'del_contact':
                        logger.debug('got del contact')
                        self.msgs[json_data['user_login']] = self.del_contact(json_data['user_id'],
                                                                         json_data['user_login'])
                        self.send_to_user()

            except:
                logger.error('recieve error')
                self.client_logout(client_name)
                self.clients.remove(client)
                exit = False

    def get_socket(self):
        """Создание подключения"""
        s = socket(AF_INET, SOCK_STREAM)
        s.bind((self.ip, self.port))
        s.settimeout(0.5)

        s.listen(10)

        return s

    def del_contact(self, nickname, name):
        """Удаление контакта"""
        try:
            contact = self.session.query(Client_table).filter_by(name=nickname).first()
            if contact is None:
                answer = json.dumps({'response': 400, 'alert': f'{nickname} not in contacts'})
                return answer

            try:
                del_contact = self.session.query(Client_list).filter_by(contact_id=contact.id).first()
                self.session.delete(del_contact)
                self.session.commit()
                answer = json.dumps({'response': 200, 'alert': f'{nickname} deleted from contacts'})
            except:
                answer = json.dumps({'response': 400, 'alert': f'{nickname} not in your contacts'})
            return answer

        except BaseException as e:
            logger.error(e)
            return 'error'

    def add_contact(self, nickname, name):
        """Добавление контакта"""
        try:
            new_contact = self.session.query(Client_table).filter_by(name=nickname).first()
            if new_contact is None:
                new_contact = Client_table(name=nickname, is_active=False)
                self.session.add(new_contact)
                self.session.commit()
            else:
                checking = self.session.query(Client_list).filter_by(contact_id=new_contact.id).first()
                if checking is None:
                    host = self.session.query(Client_table).filter_by(name=name).first()
                    contact_for_list = Client_list(host.id, new_contact.id)
                    self.session.add(contact_for_list)
                    self.session.commit()
                    answer = json.dumps({'response': 200, 'alert': f'{nickname} add into contacts'})
                else:
                    answer = json.dumps({'response': 400, 'alert': 'Already in contacts'})
            return answer
        except BaseException as e:
            logger.error(e)
            return 'error'

    def client_contact_list(self, name):
        """Формирует список контактов клиента"""
        try:
            host = self.session.query(Client_table).filter_by(name=name).first()
            client_list = self.session.query(Client_list).filter_by(host_id=host.id).all()
            result = []
            for client in client_list:
                contact = self.session.query(Client_table).filter_by(id=client.contact_id).first()
                if contact is None:
                    break
                result.append(contact.name)
            return result
        except:
            logger.error('DataBase error')
            return result.append('error')

    def client_logout(self, name):
        """Фиксирует выход клиента"""
        try:
            client = self.session.query(Client_table).filter_by(name=name).first()
            client.is_active = False
            print('Session. Changes:', self.session.dirty)
            self.session.commit()

        except:
            self.session.rollback()

    def client_login(self, name, ip):
        """Фиксирует вход клиента"""
        #with self.lock:
        try:
            client = self.session.query(Client_table).filter_by(name=name).first()
            if client is None:
                client = Client_table(name)
                self.session.add(client)

            client.is_active = True
            client_history = Client_history(ip, client.name)

            self.session.add(client)
            self.session.add(client_history)

            print('Session. New objects:', self.session.new)
            self.session.commit()

        except:
            return logger.error('Basedata error')

if __name__=='__main__':
    server = Server(port, ip, database)
    server.run()
    # thr_run = threading.Thread(target=server.run, args=())
    # thr_run.start()



