'''Написать функцию host_ping(), в которой с помощью утилиты ping
будет проверяться доступность сетевых узлов. Аргументом функции является список,
в котором каждый сетевой узел должен быть представлен именем хоста или ip-адресом.
В функции необходимо перебирать ip-адреса и проверять их доступность с выводом соответствующего
сообщения («Узел доступен», «Узел недоступен»). При этом ip-адрес сетевого узла должен
создаваться с помощью функции ip_address().'''
import subprocess
import ipaddress
import re
from tabulate import tabulate

def host_range_ping(ip, count):
    result = []
    #Октеты
    first, second, third, forth=ip.split('.')
    try:
        ip=ipaddress.ip_address(ip)

    except BaseException:
        print('Некорректный ip адрес')
        return result
    if 255-int(forth)<=count:
        print('Некорректный диапазон ip')
        return result
    last_ip=ip+count
    while 1:
        if ip==last_ip:
            print(result)
            return result

        result.append(ip)
        ip+=1




def host_ping(args):
    for arg in args:
        try:
            ip=ipaddress.ip_address(arg)
        except:
            ip=arg
#Method 1
        subprog_ping=subprocess.Popen(['ping ', str(ip)], shell=False, stdout=subprocess.PIPE)
        subprog_ping.wait()
        if subprog_ping.returncode==0:
            print(f'Узел {ip} доступен')
        else:
            print(f'Узел {ip} недоступен')
#Метод 2
        result = subprog_ping.stdout.read()
        result = result.decode('cp866').encode('utf-8').decode('utf-8')
        looses = re.findall(r'(\d+)%', result)
        if int(looses[0]) < 50:
            print(f'Узел {ip} доступен, Потери {looses[0]}%')
        else:
            print(f'Узел недоступен, , Потери {looses[0]}%')
# Метод 3
        command = ['ping', '-n', '1', str(ip)]
        if subprocess.call(command) == 0:
            print(f'Узел {ip} доступен')
        else:
            print('Узел недоступен')

def host_range_ping_tab(args):
    result={'Reachable':[], 'Unreachable':[]}

    for arg in args:
        try:
            ip = ipaddress.ip_address(arg)
            subprog_ping = subprocess.Popen(['ping ', str(ip)], shell=False, stdout=subprocess.PIPE)
            subprog_ping.wait()
            if subprog_ping.returncode == 0:
                result['Reachable'].append(ip)
            else:
                result['Unreachable'].append(ip)
        except:
            print('Некорректный ip адрес')
    print(tabulate(result, headers='keys'))


args=['80.0.1.1', '2.2.2.2','80.0.1.10', '192.168.0.100', '192.168.0.101']
#host_ping(args)

host_range_ping('80.0.1.1', 10)

# host_ping(host_range_ping('192.168.0.250', 3))

host_range_ping_tab(host_range_ping('80.0.1.1', 10))