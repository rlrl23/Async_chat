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
from sqlalchemy import create_engine, update
from Database_creation import Client_history, Client_table, Client_list
from sqlalchemy.orm import sessionmaker, query



port=7777
host='localhost'

class Server(metaclass=ServerVerify):

    def log(func):
        @wraps(func)
        def call(*args, **kwargs):
            main_func=inspect.stack()[-2][-3]
            logger.debug(f'Func {func.__name__}{args, kwargs} was called from {main_func}')
            return func(*args, **kwargs)
        return call

    @log
    def send_to_all(msgs, w):
        try:
            group_messages= msgs['all']
            for msg in group_messages:
                for c in w:
                    try:
                        c.send(msg.encode('utf-8'))
                        logger.debug(f'{msg} is sent')
                    except:
                        c.close()
                        clients.remove(c)
                        logger.error('Клиент отключился')
            msgs.pop('all')
        except BaseException as e:
            logger.error(e)

    def send_to_user(names, msgs, clients):
        for key in msgs:
            if key in names:
                msg=msgs[key]
                client=names[key]
                for m in msg:
                    client.send(m.encode('utf-8'))
                    logger.debug(f'{msg} is sent')
            else:
                logger.error('Такого пользователя в чате нет')

    def recieve(self, r, names, clients, client_host_port):
        msgs= {}
        for client in r:
            try:
                data = client.recv(100000)
                try:
                    data=data.decode('utf-8')
                    data= data.replace('}{', '};{')
                    msgs_in_data=data.split(';')
                    for msg in msgs_in_data:
                        json_data = json.loads(msg)
                        if json_data['action'] == 'presence':
                            logger.debug('got presence')
                            names[json_data['user']['name']]=client

                            self.client_login(Server, json_data['user']['name'], ip=str(client_host_port[client]))

                            msgs[json_data['user']['name']]=[json.dumps({'response': 200, 'alert': 'ok'})]

                        elif json_data['action'] == 'msg':
                            logger.debug('got message')
                            try:
                                msgs[json_data['to_user']].append(json_data['text'] + ' from ' + json_data['user']['name'])
                            except:
                                msgs[json_data['to_user']] = [json_data['text'] + ' from ' + json_data['user']['name']]
                    return msgs, names
                except:
                    json_data = json.loads(data)
                    if json_data['action'] == 'presence':
                        logger.debug('got presence')
                        names[json_data['user']['name']] = client

                        self.client_login(Server, json_data['user']['name'], ip=str(client_host_port[client]))

                        msgs[json_data['user']['name']]=[json.dumps({'response': 200, 'alert': 'ok'})]

                    elif json_data['action'] == 'msg':
                        logger.debug('got message')
                        try:
                            msgs[json_data['to_user']].append(json_data['text'] + ' from ' + json_data['user']['name'])
                        except:
                            msgs[json_data['to_user']]=[(json_data['text'] + ' from ' + json_data['user']['name'])]
                    return msgs, names

            except BaseException as e:
                for key, val in names.items():
                    if val==client:
                        self.client_logout(Server, key)
                logger.error(e)
                clients.remove(client)
                return msgs, names

    def get_socket(port):
        s=socket(AF_INET, SOCK_STREAM)
        s.bind(('', port))
        s.listen(5)
        return s

    def client_logout(self, name):
        engine = create_engine('sqlite:///server_base.db3', echo=True)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            client = session.query(Client_table).filter_by(name=name).first()
            client.is_active=False
            print('Session. Changes:', session.dirty)
            session.commit()

            # stmt = (update(Client_table).where(Client_table.name==name).values(is_active=False))
            # session.execute(stmt, execution_options={"synchronize_session": False})

        except:
            session.rollback()

    def client_login(self, name, ip):
        engine = create_engine('sqlite:///server_base.db3', echo=True)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            client= session.query(Client_table).filter_by(name=name).first()
            if client is None:
                client = Client_table(name, ip)
                session.add(client)
            client_history = Client_history(client.ip)

            session.add(client_history)

            print('Session. New objects:', session.new)
            session.commit()

        except:
            return logger.error('Basedata error')

if __name__=='__main__':

    s= Server.get_socket(port)
    clients=[]
    client_host_port={}
    names={}
    while 1:
        try:
            client, addr = s.accept()
            logger.debug(f'Запрос получен от {str(addr)}')
            client_host_port[client]=addr
            clients.append(client)
            r = []
            w = []
            try:
                if clients:
                    r, w, e = select.select(clients, clients, [], 10)
                    r=clients
            except:
                pass
            while 1:
                try:
                    if r:
                        msgs, names = Server.recieve(Server, r, names, clients, client_host_port)
                    if 'all' in msgs:
                        Server.send_to_all(msgs, w)
                    if msgs:
                        Server.send_to_user(names, msgs, clients)
                except:
                    break
        except OSError as e:
            logger.error(e)


