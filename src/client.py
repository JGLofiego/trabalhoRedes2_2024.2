import socket
import threading
import time
from crypto import gerar_chave_publica_e_privada, cifrar_texto, encode_message

SERVER_HOST = "localhost"
PORT = 3000

public_key, private_key = gerar_chave_publica_e_privada()
n, e = public_key

def reconnect():
    while True:
        try:
            print("Tentando reconectar...")
            client = socket.create_connection((SERVER_HOST, PORT))
            print("Conexão restabelecida!")
            return client
        except:
            time.sleep(5)

try:
    client = socket.create_connection((SERVER_HOST, PORT))
    print("Conexão estabelecida!")
except:
    client = reconnect()

def receive(client: socket.socket):
    global n, e  # Atualizar as variáveis globais para a chave pública recebida
    while True:
        try:
            message = client.recv(1024).decode("utf-8")
            
            # Receber chave pública do servidor
            if "," in message and len(message.split(",")) == 2:
                n, e = map(int, message.split(","))
                print(f"Chave pública recebida do servidor: n={n}, e={e}")
                continue

            # Processar mensagens normais
            if message == "REGISTER_OR_LOGIN":
                choice = input("Digite 'REGISTER' para cadastrar ou 'LOGIN' para logar: ")
                client.send(choice.encode("utf-8"))

            elif message == "USERNAME":
                username = input("Digite o nome de usuário: ")
                client.send(username.encode("utf-8"))

            elif message == "PASSWORD":
                password = input("Digite a senha: ")
                client.send(password.encode("utf-8"))

            elif message == "USER_EXISTS":
                print("Usuário já existe. Tente novamente.")

            elif message == "REGISTER_SUCCESS":
                print("Cadastro realizado com sucesso!")
                thread_wrt = threading.Thread(target=write, args=(client,))
                thread_wrt.start()

            elif message == "USER_NOT_FOUND":
                print("Usuário não encontrado. Tente novamente.")

            elif message == "INVALID_PASSWORD":
                print("Senha incorreta. Tente novamente.")

            elif message == "LOGIN_SUCCESS":
                print("Login realizado com sucesso!")
                thread_wrt = threading.Thread(target=write, args=(client,))
                thread_wrt.start()

            else:
                print(message)
        except Exception as ex:
            print(f"Erro: {ex}")
            client.close()
            client = reconnect()
            
def verificar_tamanho_unicode(mensagem):
    for char in mensagem:
        if ord(char) > 0x10FFFF:
            raise ValueError(f"Caractere inválido encontrado: {char}")


def write(client: socket.socket):
    while True:
        try:
            message = input("Digite sua mensagem: ")
            verificar_tamanho_unicode(message)
            encrypted_message = cifrar_texto(message, e, n)  # Usar a chave pública recebida do servidor
            encrypted_message_str = encode_message(encrypted_message)
            client.send(encrypted_message_str.encode("utf-8"))
        except EOFError:
            print("Mensagem inválida.")
        except OSError:
            print("Não foi possível enviar mensagem.")
            break



thread_rcv = threading.Thread(target=receive, args=(client,))
thread_rcv.start()
