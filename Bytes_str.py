task_1 = ['разработка', 'сокет', 'декоратор']
for i in task_1:
    print(i)
    print(type(i))
    b=i.encode('utf-8')
    print(b)
    print(type(b))


task_2=[b'class', b'function', b'method']
for word in task_2:
    print(type(word), len(word), word)

task_3=['attribute', 'класс', 'функция', 'type']
for i in task_3:
    b=i.encode('utf-8')
    print(b)
#всё можно записать в байтовом типе

task_4=['разработка','администрирование', 'protocol', 'standard']
for i in task_4:
    b= i.encode('utf-8')
    print(b)
    print(b.decode('utf-8'))

#task5
import subprocess
args=['ping','yandex.ru']
subprog_ping=subprocess.Popen(args, stdout=subprocess.PIPE)
for line in subprog_ping.stdout:
    line=line.decode('cp866').encode('utf-8')
    print(line.decode('utf-8'))
args=['ping','youtube.com']
subprog_ping=subprocess.Popen(args, stdout=subprocess.PIPE)
for line in subprog_ping.stdout:
    line=line.decode('cp866').encode('utf-8')
    print(line.decode('utf-8'))

#task6
with open('test_file.txt', mode='r') as f:
    print(f.encoding)
    for line in f:
        print(line)
with open('test_file.txt', mode='r', encoding='utf-8') as f:
    print(f.encoding)
    for line in f:
        print(line)
