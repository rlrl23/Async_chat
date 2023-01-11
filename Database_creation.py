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
                     Column('ip', String),


)

client_history=Table('Client_history', metadata,
                     Column('id', Integer, primary_key=True),
                     Column('come_in', DATETIME),
                     Column('ip', ForeignKey('Client.ip')),
                     )

client_list=Table('Client_list', metadata,
                  Column('id', Integer, primary_key=True),
                  Column('client_id', ForeignKey('Client.id')))

metadata.create_all(engine)


class Client_table:
    def __init__(self, name, ip, is_active=True):
        self.name = name
        self.ip = ip
        self.is_active=is_active


class Client_history:
    def __init__(self, ip):
        self.ip = ip
        self.come_in = datetime.now()

class Client_list:
    def __init__(self, client_id):
        self.client_id = client_id

mapper(Client_table, client_table)
mapper(Client_history, client_history)
mapper(Client_list, client_list)

