import dis

class ClientVerify(type):
    def __init__(self, clsname, bases, clsdict):
        error = 0
        socket = 0

        for val in clsdict.values():
            try:
                for arg in dis.get_instructions(val):
                    if arg.argval == 'accept' or arg.argval == 'listen':
                        error = 1
                        print('Ненадлежащие функции для клиента (accept или listen)')
                        break
                    elif arg.argval == 'socket':
                        socket = 1
                        print('Socket was used')
            except: pass
        if socket == 1 and error == 0:
            print('Проверка пройдена успешно')

class ServerVerify(type):
    def __init__(self, clsname, bases, clsdict):
        error=0
        socket=0
        for val in clsdict.values():
            try:
                for arg in dis.get_instructions(val):

                    if arg.argval=='connect':
                        error=1
                        print('Ненадлежащая функция для сервера (connect)')
                        break
                    elif arg.argval=='socket':
                        socket = 1
                        print('Socket was used')
            except:pass
        if socket==1 and error==0:
            print('Проверка пройдена успешно')

