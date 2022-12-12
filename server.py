from socket import *
import json
import logging
import time
import log.server_log_config
from functools import wraps
import inspect

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
def send(msg, client):
    try:
        client.send(msg.encode('utf-8'))
        logger.debug(f'{msg} is sent')
    except BaseException as e:
        logger.error(e)

def main123():
    send(msg, client)


def recieve(client):
    try:
        data = client.recv(10000)
        if json.loads(data)['action'] == 'presence':
            logger.debug('got presence')
            return json.dumps({'response': 200, 'alert': 'ok'})
        elif json.loads(data)['action'] == 'msg':
            logger.debug('got message')
            return json.dumps({'response': 200, 'alert': 'ok'})
    except BaseException as e:
        logger.error(e)
        return json.dumps({'response': 400, 'alert': 'error'})



def get_socket(port):
    s=socket(AF_INET, SOCK_STREAM)
    s.bind(('', port))
    s.listen(5)
    return s

if __name__=='__main__':
    s= get_socket(port)
    while True:
        try:
            client, addr = s.accept()

            logger.debug(f'Запрос получен от {str(addr)}')

            msg = recieve(client)

            #send(msg, client)
            main123()

            client.close()

        except OSError as e:
            logger.error(e)


