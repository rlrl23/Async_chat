from subprocess import Popen, CREATE_NEW_CONSOLE

if __name__=='__main__':
    p_list = []
    while True:
        user = input("Запустить 2 клиентов (2) / Закрыть клиентов (x) / Выйти (q) ")
        if user == 'q':
            break
        elif user == 'x':
            for p in p_list:
                p.kill()
                p_list.clear()
        else:
            p_list.append(Popen(['python', 'client_read.py'], creationflags=CREATE_NEW_CONSOLE))
            p_list.append(Popen(['python','client_write.py'], creationflags=CREATE_NEW_CONSOLE))

            print(f' Запущено 2 клиента')
