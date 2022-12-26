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

    def recieve(r,names, clients):
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
                        msgs[json_data['user']['name']]=[json.dumps({'response': 200, 'alert': 'ok'})]

                    elif json_data['action'] == 'msg':
                        logger.debug('got message')
                        try:
                            msgs[json_data['to_user']].append(json_data['text'] + ' from ' + json_data['user']['name'])
                        except:
                            msgs[json_data['to_user']]=[(json_data['text'] + ' from ' + json_data['user']['name'])]
                    return msgs, names

            except BaseException as e:
                logger.error(e)
                clients.remove(client)
                return msgs, names

    def get_socket(port):
        s=socket(AF_INET, SOCK_STREAM)
        s.bind(('', port))
        s.listen(5)
        return s

if __name__=='__main__':

    s= Server.get_socket(port)
    clients=[]
    names={}
    while 1:
        try:
            client, addr = s.accept()

            logger.debug(f'Запрос получен от {str(addr)}')

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
                        msgs, names = Server.recieve(r,names, clients)
                    if 'all' in msgs:
                        Server.send_to_all(msgs, w)
                    if msgs:
                        Server.send_to_user(names, msgs, clients)
                except:
                    break
        except OSError as e:
            logger.error(e)


