# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'client.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets, QtSql
from Client_database_creation import Contact, Msg_history, Contact_list
from sqlalchemy import create_engine, desc, or_, and_
from sqlalchemy.orm import sessionmaker, query
from client_2 import Client
import threading
import datetime
import time
import json
from PyQt5 import QtCore, QtGui, QtWidgets
import logging
import log.client_log_config

logger=logging.getLogger('client')

socket_lock = threading.Lock()

class Ui_chatWindow(object):

    def setupUi(self, chatWindow):
        """ Main window"""
        chatWindow.setObjectName("chatWindow")
        chatWindow.resize(555, 444)

        self.User = Client(enter_ui.user_name.text(), 7777, 'localhost', enter_ui.user_password.text())
        self.User.send(self.User.create_presence_msg())

        self.session = self.User.session

        thr_recieve = threading.Thread(target=self.User.recieve, args=(), daemon=1)
        thr_recieve.start()

        self.chat_is_open = False

        self.centralwidget = QtWidgets.QWidget(chatWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(20, 30, 160, 271))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")

        self.contact_list = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.contact_list.setContentsMargins(0, 0, 0, 0)
        self.contact_list.setObjectName("contact_list")

        self.contact_list_2 = QtWidgets.QListWidget(self.verticalLayoutWidget)
        self.contact_list_2.setObjectName("contact_list_2")
        self.contact_list.addWidget(self.contact_list_2)
        self.contact_list_2.addItems(self.db_contact_list())
        self.contact_list_2.itemDoubleClicked.connect(self.on_2Clicked)

        self.text_enter = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.text_enter.setGeometry(QtCore.QRect(20, 300, 431, 71))
        self.text_enter.setObjectName("text_enter")

        self.btn_add_contact = QtWidgets.QPushButton(self.centralwidget)
        self.btn_add_contact.setGeometry(QtCore.QRect(20, 10, 161, 23))
        self.btn_add_contact.setObjectName("btn_add_contact")
        self.btn_add_contact.clicked.connect(self.add_new_contact)

        self.chat = QtWidgets.QTextBrowser(self.centralwidget)
        self.chat.setGeometry(QtCore.QRect(180, 30, 331, 271))
        self.chat.setObjectName("chat")

        self.btn_send = QtWidgets.QPushButton(self.centralwidget)
        self.btn_send.setGeometry(QtCore.QRect(450, 300, 61, 71))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setUnderline(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        self.btn_send.setFont(font)
        self.btn_send.setObjectName("btn_send")
        self.btn_send.clicked.connect(self.send_msg)

        chatWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(chatWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 555, 21))
        self.menubar.setObjectName("menubar")
        chatWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(chatWindow)
        self.statusbar.setObjectName("statusbar")
        chatWindow.setStatusBar(self.statusbar)

        self.retranslateUi(chatWindow)
        QtCore.QMetaObject.connectSlotsByName(chatWindow)

    def retranslateUi(self, chatWindow):
        _translate = QtCore.QCoreApplication.translate
        chatWindow.setWindowTitle(_translate("chatWindow", "MainWindow"))
        self.btn_add_contact.setText(_translate("chatWindow", "+      New contact"))
        self.btn_send.setText(_translate("chatWindow", ">"))

    def db_contact_list(self):
        result = []
        contact_list = self.session.query(Contact_list).all()
        for line in contact_list:
            contact = self.session.query(Contact).filter_by(id=line.contact_id).first()
            result.append(contact.name)
        return result

    def client_history(self):
        contact = self.session.query(Contact).filter_by(name=self.chat_is_open).first()
        msgs = self.session.query(Msg_history).filter(and_(
                                                      or_(Msg_history.from_==self.User.name, Msg_history.from_==contact.name),
                                                      or_(Msg_history.to_==contact.name, Msg_history.to_==self.User.name))).order_by(desc(Msg_history.id)).limit(6)
        self.chat.setText('')
        msg_list=[]
        for msg in msgs:
            msg= msg.msg +'\n'+str(msg.time.replace(microsecond=0))+ ' from '+msg.from_+'\n\n'
            msg_list.append(msg)
        for msg in msg_list[::-1]:
            self.chat.setText(self.chat.toPlainText() + msg)

    def on_2Clicked(self, item):
        self.chat_is_open=item.text()
        self.client_history()

    def send_msg(self):
        if self.chat_is_open:
            #self.chat.setText(self.chat.toPlainText()+ self.text_enter.toPlainText()+'\n'+str(datetime.datetime.now())+' from '+Mary.name+'\n\n')
            self.User.send(self.User.create_msg(self.chat_is_open, self.text_enter.toPlainText()))
            msg= self.text_enter.toPlainText()+'\n'+str(datetime.datetime.now().replace(microsecond=0))+' from '+self.User.name+'\n\n'
            self.chat.setText(self.chat.toPlainText()+ msg)

            self.text_enter.setPlainText('')

    def add_new_contact(self):
        text, ok = QtWidgets.QInputDialog.getText(chatWindow, 'Add form', 'Name of new contact')
        if ok:
            self.contact_list_2.addItem(str(text))
            self.User.send(self.User.add_contact(text))


    def recieve(self):
        time.sleep(2)
        while True:
            try:
                data = self.User.s.recv(10000)
                logger.debug(f'The message {data.decode("utf-8")} is recieved ')
                data = data.decode("utf-8")
                data = data.replace('}{', '};{')
                msgs_in_data = data.split(';')
                for msg in msgs_in_data:
                    json_data = json.loads(msg)
                    if json_data.get('action'):
                        self.User.add_msg_in_history(json_data, False)
                        if self.chat_is_open==json_data['user']['name'] or self.chat_is_open=='all':
                            self.chat.setText(self.chat.toPlainText() + json_data['text'])
                        self.client_history()
                        new_msg = QtWidgets.QMessageBox(chatWindow)
                        new_msg.setWindowTitle("from "+ str(json_data['user']['name']))
                        new_msg.setText(json_data['text'])
                        new_msg.setStandardButtons(QtWidgets.QMessageBox.Cancel)

                        new_msg.exec_()
            except BaseException as e:
                logger.error(e)
                logger.debug(f'recieve finished')
                break

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        """ Login window"""
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)

        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.lable_name = QtWidgets.QLabel(Dialog)
        self.lable_name.setGeometry(QtCore.QRect(40, 50, 81, 41))
        self.lable_name.setObjectName("lable_name")
        self.user_name = QtWidgets.QLineEdit(Dialog)
        self.user_name.setGeometry(QtCore.QRect(150, 60, 221, 31))
        self.user_name.setObjectName("user_name")

        self.lable_password = QtWidgets.QLabel(Dialog)
        self.lable_password.setGeometry(QtCore.QRect(40, 110, 81, 41))
        self.lable_password.setObjectName("lable_password")
        self.user_password = QtWidgets.QLineEdit(Dialog)
        self.user_password.setGeometry(QtCore.QRect(150, 110, 221, 31))
        self.user_password.setObjectName("user_password")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(self.enter)

        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.lable_name.setText(_translate("Dialog", " login"))
        self.user_name.setText('Mary')
        self.lable_password.setText(_translate("Dialog", " password"))
        self.user_password.setText('1234')

    def enter(self):
        if self.user_name.text()!='':

            ui.setupUi(chatWindow)
            chatWindow.show()
            enterWindow.close()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    chatWindow = QtWidgets.QMainWindow()
    ui = Ui_chatWindow()

    enterWindow= QtWidgets.QDialog()
    enter_ui=Ui_Dialog()
    enter_ui.setupUi(enterWindow)
    enterWindow.show()

    sys.exit(app.exec_())
