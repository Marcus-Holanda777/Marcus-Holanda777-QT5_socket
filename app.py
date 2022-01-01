from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import QThread
import socket
import threading
import os
import sys
from collections import deque
import sys
from Designer import Ui_MainWindow
from time import sleep
from auxiliar import *


class Cliente:
    def __init__(self, maquina='localhost', porta=50000):
        self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.maquina = maquina
        self.porta = porta
        self.cache_cliente = deque(maxlen=5)
        self.cache_servidor = deque(maxlen=5)
        self.usuario = os.environ['USERNAME']

        self.main()

    def enviar_mensagem(self, escolha):
        comando = menu[escolha][1]

        self.cache_cliente.appendleft(comando)
        self.cliente.send(f'{self.usuario},{comando}'.encode('utf_8'))

    def receber_mensagem(self):
        while True:
            try:
                msg = self.cliente.recv(2048).decode('utf_8')
                self.cache_servidor.appendleft(msg)
            except Exception as e:
                self.fechar()
                break

    def rodar_logs(self, escolha):
        conn_01 = threading.Thread(
            target=self.receber_mensagem)
        conn_02 = threading.Thread(
            target=self.enviar_mensagem, args=[escolha])

        conn_01.start()
        conn_02.start()

    def main(self):
        try:
            self.cliente.connect((self.maquina, self.porta))
            self.cliente.send(f'Conectado .. {self.usuario}'.encode('utf_8'))
        except Exception as e:
            print(e)
            print('Nao foi possivel conectar !')
            self.cliente.close()

    def fechar(self):
        self.cliente.close()


class Back(QThread):
    update_consulta = None

    def run(self):
        while True:
            self.update_consulta()
            sleep(2)


class App(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        super().setupUi(self)

        ''' ESTILO DA LISTVIEW '''
        self.listCliente.setStyleSheet(estilo_cliente)
        self.listServidor.setStyleSheet(estilo_servidor)

        ''' ESTILO BUTAO '''
        self.btnExec.setStyleSheet(estilo_btn_exe)

        ''' COMPOSICAO COM A CLASE CLIENTE '''
        self.cliente = Cliente()

        ''' PARALELO '''
        self.back = Back()
        self.back.start()
        self.back.update_consulta = self.update_lista

        ''' CARREGANDO AS FUNCOES '''
        self.carrega_combo_tarefa()

        self.listCliente.setDisabled(True)
        self.listServidor.setDisabled(True)

        ''' COMANDO DOS BOTOES '''
        self.btnExec.clicked.connect(self.btn_executar)

    def carregar_cliente(self):
        self.listCliente.clear()

        for row in self.cliente.cache_cliente:
            self.listCliente.addItem(row)

    def carregar_servidor(self):
        self.listServidor.clear()

        for row in self.cliente.cache_servidor:
            self.listServidor.addItem(row)

    def carrega_combo_tarefa(self):

        for k, v in menu.items():
            self.comboTarefas.addItem(f'{k}: {v[0]}')

    def btn_executar(self):
        resposta = QMessageBox.warning(self, 'OK',
                                       'Deseja executar ?',
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)

        if resposta == QMessageBox.Yes:
            selecionado = self.comboTarefas.currentText()
            selecionado = selecionado.split(':')[0].strip()

            self.cliente.rodar_logs(selecionado)

    def update_lista(self):
        self.carregar_cliente()
        self.carregar_servidor()

    def closeEvent(self, event):
        reply = QMessageBox.critical(self, 'Sair ?',
                                     'Deseja Realmente sair ?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            if not type(event) == bool:
                self.cliente.fechar()
                event.accept()

            else:
                sys.exit()

        else:
            if not type(event) == bool:
                event.ignore()


if __name__ == '__main__':
    qt = QApplication(sys.argv)
    app = App()
    app.show()
    qt.exec_()
