import select
import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QDialog, QHBoxLayout, QMessageBox, QPushButton, QSplitter, QTextBrowser, QVBoxLayout, QWidget, QGridLayout, QLabel, QLineEdit, QTextEdit)
from utils import *
import threading
import os
import ssl

SERVER_HOST = 'localhost'
client = ''


stop_thread = False

def get_and_send(client):
    while not stop_thread:
        data = sys.stdin.readline().strip()
        if data: 
            send(client.sock, data)

def determineType(data):
    messageType = data.split("|")
    print(messageType)

class LoginScreen(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.w = None
        self.logingrid = QGridLayout()
        self.setLayout(self.logingrid)
        self.logingrid.addWidget(QLabel('IP Address'), 1, 0)
        self.logingrid.addWidget(QLabel('Port'), 2, 0)
        self.logingrid.addWidget(QLabel('Nick Name'), 5, 0)
        self.ipText = QLineEdit()
        self.portText = QLineEdit()
        self.nameText = QLineEdit()
        self.logingrid.addWidget(self.ipText, 1, 1)
        self.logingrid.addWidget(self.portText, 2, 1)
        self.logingrid.addWidget(self.nameText, 5, 1)
        self.btn1 = QPushButton(self)
        self.btn1.setText('Connect')
        self.btn1.clicked.connect(self.attemptLogin)
        self.btn2 = QPushButton(self)
        self.btn2.setText("Cancel")
        self.btn2.clicked.connect(self.cancelQuit)

        self.logingrid.addWidget(self.btn2,6,2)
        self.logingrid.addWidget(self.btn1,6,1)
        self.setWindowTitle('Login')
        self.setGeometry(400, 400, 300, 200)
        self.setFixedSize(300,200)
        self.show() 
    
    def cancelQuit(self):
        os._exit(1)
    def attemptLogin(self):
        #for i in reversed(range(self.logingrid.count())): 
        #    self.logingrid.itemAt(i).widget().deleteLater()
        #self.logingrid.deleteLater()
        try:
            #print("login success")
            global client 
            client = ChatClient(self.nameText.text(), int(self.portText.text()),self.ipText.text())
            self.btn1.setEnabled(False)
            self.w = MessageScreen()
            self.w.show()
            #client.run()
            #threading.Thread(target=client.run()).start()
            
            #self.initUI()
        
        except:
            tryAgain = QMessageBox(self)
            tryAgain.setWindowTitle("Issue!!")
            tryAgain.setText("Please Try Again")
            button = tryAgain.exec()
       

class MessageScreen(QDialog):
    def __init__(self):
        super().__init__()
        #layout = QVBoxLayout()
        self.label = QLabel("Another Window ")
        #layout.addWidget(self.label)
        #self.setLayout(layout)
        self.text = QTextBrowser(self) 
        self.text.setGeometry(10, 10, 300, 100)
        self.text2 = QLineEdit(self)
        self.text2.setPlaceholderText(u'type here')
        self.text2.setGeometry(10, 160, 300, 30)
        self.button = QPushButton('Send', self)
        self.button.setGeometry(250, 210, 60, 30)
        self.button.clicked.connect(self.sendButton)
        self.button2 = QPushButton('Cancel', self)
        self.button2.setGeometry(150, 210, 60, 30)
        self.button2.clicked.connect(self.cancelQuit)
        self.setFixedSize(320,250)
        self.init()
    def sendButton(self):
        self.text.append(self.text2.text())
        toSend = self.text2.text()
        toSend += " "
        send(client.sock, toSend)
        self.text2.clear()

    def init(self):
        #client.run() 
        #threading.Thread(target=client.run).start()
        threading.Thread(target=client.run, args=(self,)).start()
        #print("login success")
    def cancelQuit(self):
        os._exit(1)

class ChatClient():
    """ A command line chat client using select """
    def __init__(self, name, port, host):
        self.name = name
        self.connected = False
        self.host = host
        self.port = port
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        # Initial prompt
        self.prompt = f'[{name}@{socket.gethostname()}]> '
        
        # Connect to server at port
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock = self.context.wrap_socket(self.sock, server_hostname=host)
            self.sock.connect((host, self.port))


            print(f'Now connected to chat server@ port {self.port}')
            self.connected = True
            
            # Send my name...
            send(self.sock, 'NAME: ' + self.name)
            data = receive(self.sock)
            
            # Contains client address, set it
            addr = data.split('CLIENT: ')[1]
            self.prompt = '[' + '@'.join((self.name, addr)) + ']> '

            threading.Thread(target=get_and_send, args=(self,)).start()
            #threading.Thread(target=self.run(), args=(self,)).start()
            print("Check")
        except socket.error as e:
            print(f'Failed to connect to chat server @ port {self.port}')
            sys.exit(1)

    def cleanup(self):
        """Close the connection and wait for the thread to terminate."""
        self.sock.close()

    def run(self,qwindow):
        """ Chat client main loop """
        while self.connected:
            try:
                sys.stdout.write(self.prompt)
                sys.stdout.flush()

                # Wait for input from stdin and socket
                # readable, writeable, exceptional = select.select([0, self.sock], [], [])
                readable, writeable, exceptional = select.select(
                    [self.sock], [], [])

                for sock in readable:

                    if sock == self.sock:
                        data = receive(self.sock)
                        if not data:
                            print('Client shutting down.')
                            self.connected = False
                            break
                        else:

                            #check type of data
                            determineType(data)
                            qwindow.text.append(data)
                            #sys.stdout.flush()

            except KeyboardInterrupt:
                print(" Client interrupted. " "")
                stop_thread = True
                self.cleanup()
                break





if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LoginScreen()
    
    sys.exit(app.exec_())