# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from Database_creation import Client_table, Client_history
from sqlalchemy.orm import sessionmaker, query
from sqlalchemy import create_engine
from server import Server

class Ui_MainWindow(object):
    """Main window"""
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.btn_client_list = QtWidgets.QPushButton(self.centralwidget)
        self.btn_client_list.setGeometry(QtCore.QRect(30, 10, 75, 23))
        self.btn_client_list.setObjectName("client_list")
        self.btn_client_list.clicked.connect(self.client_list)

        self.btn_history = QtWidgets.QPushButton(self.centralwidget)
        self.btn_history.setGeometry(QtCore.QRect(320, 10, 75, 23))
        self.btn_history.setObjectName("client_history")
        self.btn_history.clicked.connect(self.client_history)

        self.btn_server = QtWidgets.QPushButton(self.centralwidget)
        self.btn_server.setGeometry(QtCore.QRect(570, 320, 101, 23))
        self.btn_server.setObjectName("server_settings")
        self.btn_server.clicked.connect(self.server_settings)

        self.answer=QtWidgets.QLabel(self.centralwidget)
        self.answer.setGeometry(QtCore.QRect(570, 380, 101, 23))


        self.Database = QtWidgets.QLabel(self.centralwidget)
        self.Database.setGeometry(QtCore.QRect(30, 60, 401, 481))
        self.Database.setObjectName("Database")

        self.path = QtWidgets.QLineEdit(self.centralwidget)
        self.path.setGeometry(QtCore.QRect(620, 80, 241, 31))
        self.path.setObjectName("path")

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(460, 85, 141, 21))
        self.label.setObjectName("label")

        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(460, 140, 141, 21))
        self.label_2.setObjectName("label_2")

        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(460, 200, 141, 21))
        self.label_3.setObjectName("label_3")

        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(460, 260, 141, 21))
        self.label_4.setObjectName("label_4")

        self.database_name = QtWidgets.QLineEdit(self.centralwidget)
        self.database_name.setGeometry(QtCore.QRect(620, 260, 161, 31))
        self.database_name.setObjectName("database_name")

        self.port = QtWidgets.QLineEdit(self.centralwidget)
        self.port.setGeometry(QtCore.QRect(620, 140, 161, 31))
        self.port.setObjectName("port")

        self.ip = QtWidgets.QLineEdit(self.centralwidget)
        self.ip.setGeometry(QtCore.QRect(620, 200, 161, 31))
        self.ip.setObjectName("ip")

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.btn_client_list.setText(_translate("MainWindow", "Client list"))
        self.btn_history.setText(_translate("MainWindow", "Client history"))
        self.btn_server.setText(_translate("MainWindow", "Set server settings"))
        self.label.setText(_translate("MainWindow", "Open database"))
        self.path.setText(_translate("MainWindow", "C:/Users/SV2/PycharmProjects/Async_chat"))
        self.label_2.setText(_translate("MainWindow", "Port"))
        self.label_3.setText(_translate("MainWindow", "IP"))
        self.label_4.setText(_translate("MainWindow", "Database name"))
        self.port.setText(_translate("MainWindow", "7777"))
        self.database_name.setText(_translate("MainWindow", "server_base.db3"))

    def client_list(self):
        """Show the client list"""
        engine = create_engine('sqlite:///server_base.db3', echo=True)
        Session = sessionmaker(bind=engine)
        session = Session()
        client_list = session.query(Client_table).all()
        self.Database.setText('Id'+'  ' +'Client name'+'  ' + 'Is_active'+'\n')
        for client in client_list:
            self.Database.setText(self.Database.text()+'\n'+str(client.id)+'    ' +client.name+'        '+ str(client.is_active))

    def client_history(self):
        """Show the client history"""
        engine = create_engine('sqlite:///server_base.db3', echo=True)
        Session = sessionmaker(bind=engine)
        session = Session()
        client_list = session.query(Client_history).all()
        self.Database.setText('Id' + '                ' + 'Ip' + '                                 ' + 'Come in (time)'+'                 ' + 'Client name' +  '\n')
        for client in client_list:
            self.Database.setText(
                self.Database.text() + '\n' + str(client.id) + '    ' + client.ip + '        ' + str(
                    client.come_in)+ '        ' +client.name)

    def server_settings(self):
        """Check the server settings"""
        port=self.port.text()
        ip=self.ip.text()
        database='sqlite:///'+self.path.text()+'/'+self.database_name.text()
        try:
            s = Server(int(port), ip, database)
            socket=s.get_socket()
            self.answer.setText('Settings are correct!')
            socket.close()
        except:
            self.answer.setText('Error settings!')

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
