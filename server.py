from socket import *
import json
import logging
import log.server_log_config

logger=logging.getLogger('server')

port=7777
host='localhost'

def send(msg, client):
    try:
        client.send(msg.encode('utf-8'))
        logger.debug(f'{msg} is sent')
    except BaseException as e:
        logger.error(e)

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

            send(msg, client)

            client.close()

        except OSError as e:
            logger.error(e)


