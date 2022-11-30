from socket import *
import json
port=7777
host='localhost'

def create_response_msg(data):
    try:
        if json.loads(data)['action'] == 'presence':
            return json.dumps({'response': 200, 'alert':'ok'})
    except:
        return json.dumps({'response': 400, 'alert': 'Error'})

def get_socket(port, host):
    s=socket(AF_INET, SOCK_STREAM)
    s.bind(('', port))
    s.listen(5)
    return s

if __name__=='__main__':
    s= get_socket(port, host)
    while True:
        client, addr=s.accept()
        print('Запрос получен от ', str(addr))
        data=client.recv(10000)
        msg=create_response_msg(data)
        client.send(msg.encode('utf-8'))
        client.close()