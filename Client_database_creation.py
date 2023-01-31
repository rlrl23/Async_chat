from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, create_engine, DATETIME, Boolean, Text
from sqlalchemy.orm import mapper # Mapper находится в пакете с ОРМ
#from client_2 import Client
from datetime import datetime
'''
список_контактов;
история_сообщений.
'''
engine = create_engine('sqlite:///client_base.db3')

metadata = MetaData()

contact= Table('Contact', metadata,
                     Column('id', Integer, primary_key=True),
                     Column('name', String),
)

msg_history=Table('Msg_history', metadata,
                     Column('id', Integer, primary_key=True),
                     Column('time', DATETIME),
                     Column('from_', ForeignKey('Contact.name')),
                    Column('to_', ForeignKey('Contact.name')),
                  Column('msg', Text),
                     )
contact_list=Table('Contact_list', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('host_id', ForeignKey('Contact.id')),
                    Column('contact_id', ForeignKey('Contact.id')),
                   )


metadata.create_all(engine)


class Contact:
    def __init__(self, name):
        self.name = name

class Msg_history:
    def __init__(self, from_, to_, msg):
        self.from_ = from_
        self.time = datetime.now()
        self.to_ = to_
        self.msg=msg

class Contact_list:
    def __init__(self, host_id, contact_id):
        self.host_id = host_id
        self.contact_id = contact_id

mapper(Contact, contact)
mapper(Contact_list, contact_list)
mapper(Msg_history, msg_history)

