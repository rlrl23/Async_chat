from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, create_engine, DATETIME, Boolean
from sqlalchemy.orm import mapper # Mapper находится в пакете с ОРМ
#from client_2 import Client
from datetime import datetime
'''○ клиент: ■ логин;■ информация.

○ история_клиента:■ время входа;■ ip-адрес.

○ список_контактов (составляется на основании выборки всех записей с id_владельца):
■ id_владельца;
■ id_клиента.
'''
engine = create_engine('sqlite:///server_base.db3', echo=True)

metadata = MetaData()

client_table = Table('Client', metadata,
                     Column('id', Integer, primary_key=True),
                     Column('name', String),
                    Column('is_active', Boolean),
)

client_history=Table('Client_history', metadata,
                     Column('id', Integer, primary_key=True),
                     Column('come_in', DATETIME),
                     Column('ip', String),
                        Column('name', ForeignKey('Client.name')),
                     )

client_list=Table('Client_list', metadata,
                  Column('id', Integer, primary_key=True),
                  Column('host_id', ForeignKey('Client.id')),
                    Column('contact_id', ForeignKey('Client.id'))

                  )
client_password=Table('Client_password', metadata,
                        Column('password', String),
                        Column('socket', String, primary_key=True)
)
metadata.create_all(engine)

class Client_password:
    def __init__(self, password, socket):
        self.password = password
        self.socket=socket

class Client_table:
    def __init__(self, name, is_active=True):
        self.name = name
        self.is_active=is_active


class Client_history:
    def __init__(self, ip, name):
        self.ip = ip
        self.come_in = datetime.now()
        self.name = name

class Client_list:
    def __init__(self, host_id, client_id):
        self.host_id=host_id
        self.contact_id = client_id

mapper(Client_table, client_table)
mapper(Client_history, client_history)
mapper(Client_list, client_list)
mapper(Client_password, client_password)
