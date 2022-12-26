from subprocess import Popen, CREATE_NEW_CONSOLE

if __name__=='__main__':
    p_list = []
    while True:
        user = input("Запустить n клиентов (n) / Закрыть клиентов (x) / Выйти (q) ")
        if user == 'q':
            break
        elif user == 'x':
            for p in p_list:
                p.kill()
                p_list.clear()
        else:
            for _ in range(int(user)):
                p_list.append(Popen('python time_client_random.py', creationflags=CREATE_NEW_CONSOLE))
            print(f' Запущено {user} клиента(ов)')
