from socket import *
import json
import logging
import time
import log.server_log_config
from functools import wraps
import inspect
import select

logger=logging.getLogger('server')

port=7777
host='localhost'


# def m_func(log):
#     print(m_func.__name__)
def log(func):
    @wraps(func)
    def call(*args, **kwargs):
        main_func=inspect.stack()[-2][-3]
        logger.debug(f'Func {func.__name__}{args, kwargs} was called from {main_func}')
        return func(*args, **kwargs)
    return call

@log
def send(msgs, w, clients):
    for client in w:
        try:
            for msg in msgs:
                msg=msg.encode('utf-8')
                for c in clients:
                    try:
                        c.send(msg)
                        logger.debug(f'{msg} is sent')
                    except:
                        c.close()
                        clients.remove(c)
                        logger.error('Клиент отключился')
        except BaseException as e:
            logger.error(e)


def recieve(r, clients):
    msgs=[]
    for client in r:
        try:
            data = client.recv(100000).decode('utf-8')
            try:
                data= data.replace('}{', '};{')
                msgs_in_data=data.split(';')
                for msg in msgs_in_data:
                    json_data = json.loads(msg)
                    if json_data['action'] == 'presence':
                        logger.debug('got presence')
                        return json.dumps({'response': 200, 'alert': 'ok'})
                    elif json_data['action'] == 'msg':
                        logger.debug('got message')
                        msgs.append(json_data['text'] + ' from ' + json_data['user']['name'])
                return msgs
            except:
                json_data = json.loads(data)
                if json_data['action'] == 'presence':
                    logger.debug('got presence')
                    return json.dumps({'response': 200, 'alert': 'ok'})
                elif json_data['action'] == 'msg':
                    logger.debug('got message')
                    msgs.append(json_data['text']+' from '+json_data['user']['name'])
                    return msgs
        except BaseException as e:
            logger.error(e)
            clients.remove(client)
            return json.dumps({'response': 400, 'alert': 'error'})

def get_socket(port):
    s=socket(AF_INET, SOCK_STREAM)
    s.bind(('', port))
    s.listen(5)
    return s

if __name__=='__main__':
    s= get_socket(port)
    clients=[]
    while True:
        try:
            client, addr = s.accept()

            logger.debug(f'Запрос получен от {str(addr)}')

            try:
                clients.append(client)
                r=[]
                w=[]
                r, w, e = select.select(clients, clients, [], 10)
            except:
                pass

            msgs = recieve(r, clients)
            send(msgs, w, clients)

            msgs = recieve(r, clients)
            send(msgs, w, clients)

        except OSError as e:
            logger.error(e)


