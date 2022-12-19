from subprocess import Popen, CREATE_NEW_CONSOLE

if __name__=='__main__':
    p_list = []
    while True:
        user = input("Запустить 3 клиента (s) / Закрыть клиентов (x) / Выйти (q) ")
        if user == 'q':
            break
        elif user == 's':
            for _ in range(3):
                p_list.append(Popen('python time_client_random.py', creationflags=CREATE_NEW_CONSOLE))
            print(' Запущено 3 клиента')
        elif user == 'x':
            for p in p_list:

                p.kill()
                p_list.clear()