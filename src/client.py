import socket, threading, time, os
from crypto import criptografar, descriptografar, sendEncodeMsg
from getpass import getpass


def reconnect():
    while True:
        try:
            print("Tentando reconectar...")
            client = socket.create_connection(("localhost", 3000))
            print("Conexão restabelecida!")
            break
        except:
            time.sleep(5)
            pass
    return client

SERVER_HOST = "localhost"
HOST = "127.0.0.1"
PORT = 3000

try:
    client = socket.create_connection((SERVER_HOST, PORT))
    print("Conexão estabelecida!")
except:
    client = reconnect()
    

def receive(client: socket.socket):
    auth_choice = None
    while True:
        try:
            message = client.recv(1024).decode("ascii")
            
            message = descriptografar(message)

            if message == "REGISTER_OR_LOGIN":
                auth_choice = input("Digite 'REGISTER' para cadastrar ou 'LOGIN' para logar: ")
                sendEncodeMsg(client, auth_choice)

            elif message == "USERNAME":
                username = input("Digite o nome de usuário: ")
                sendEncodeMsg(client, username)

            elif message == "PASSWORD":
                while True:
                    password = getpass("Digite a senha: ")
                    if auth_choice == "REGISTER":
                        confirm = getpass("Confirme sua senha: ")
                        if confirm != password:
                            print("Senhas não coincidem, tente novamente.")
                            continue
                    sendEncodeMsg(client, password)
                    break

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
            elif message.startswith("JOINED"):
                parts = message.split(" ", 1)
                print(f"Entrou num chat privado com {parts[1]}. Digite '/leave' caso queira sair.")
            elif message == "LEFT":
                print("Você saiu do modo privado")
            elif message == "USER_LEFT":
                print("Usuário não está mais online, voltando ao modo grupo.")
            else:
                print(message)
        except:
            print("Um erro ocorreu!")
            client.close()
            client = reconnect()

def write(client: socket.socket):
    while True:
        try:
            message = input()
            if(message.startswith("/file")):
                message, name = message.split(" ", 1)
                filename = "./arquivos_testes/"+ name
                filesize = os.path.getsize(filename)
                sendEncodeMsg(client, f"{message}, {filesize}, {filename}")
                thread_wrt = threading.Thread(target=send_file, args=(client,filename))
                thread_wrt.start()
            else:
                sendEncodeMsg(client, message)
        except EOFError:
            print("Mensagem inválida.")
        except OSError:
            print("Não foi possível enviar mensagem.")
            break

def send_file(client: socket.socket, filename: str):
    with open(filename, "rb") as f:
        while True:
            print("Enviando arquivo.")
            bytes_read = f.read(1024)
            if not bytes_read:
                print("Arquivo enviado.")
                break
            client.sendall(bytes_read)

thread_rcv = threading.Thread(target=receive, args=(client,))
thread_rcv.start()
