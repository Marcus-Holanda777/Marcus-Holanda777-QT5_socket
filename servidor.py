import socket
from subprocess import Popen
import threading
from time import sleep

HOST = 'localhost'
PORT = 50000


def resposta_fim(cliente, processo, raiz, user, comando):
    while processo.poll() is None:
        sleep(5)

    try:
        cliente.send(
            f"Server -> [OK] Finalizado: {raiz}, {comando}, {user}".encode('utf_8'))
    except Exception as e:
        print('Desconectado ...')


def rodar_scripting(cliente, endereco):
    while True:
        try:
            msg = cliente.recv(2048).decode('utf_8')

            user, raiz, comando = msg.split(',')
            print(f'Usuario: {user}, comando: {comando}, endereco: {endereco}')

            cliente.send(
                f"Server -> [OK] Comando executado: {user}, {endereco}".encode('utf_8'))

            p = Popen(comando, cwd=raiz, shell=True)

            ver = threading.Thread(target=resposta_fim, args=[
                cliente, p, raiz, user, comando])
            ver.start()

        except Exception as e:
            try:
                cliente.send(
                    'Server -> [ERRO] Comando invalido !'.encode('utf_8'))
            except Exception as e:
                print('Desconectado ...')
                break


servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    servidor.bind((HOST, PORT))
    servidor.listen()

except Exception as e:
    print('\nNão foi possivel conectar ao servidor !')
else:
    print(' ===== SERVIDOR CONECTADO =====')


while True:
    cliente, endereco = servidor.accept()

    msg = cliente.recv(2048).decode('utf_8')
    print(msg)

    rotina = threading.Thread(target=rodar_scripting,
                              args=[cliente, endereco])
    rotina.start()
