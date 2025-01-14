import socket, threading, time
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

                elif data == "REGISTER_SUCCESS":
                    print("Cadastro realizado com sucesso!")
                    thread_wrt = threading.Thread(target=write, args=(client,))
                    thread_wrt.start()

                elif data == "USER_NOT_FOUND":
                    print("Usuário não encontrado. Tente novamente.")

                elif data == "INVALID_PASSWORD":
                    print("Senha incorreta. Tente novamente.")
                    
                elif data == "LOGIN_SUCCESS":
                    print("Login realizado com sucesso!")
                    thread_wrt = threading.Thread(target=write, args=(client,))
                    thread_wrt.start()
                    
                elif data.startswith("JOINED"):
                    parts = data.split(" ", 1)
                    print(f"Entrou num chat privado com {parts[1]}. Digite '/leave' caso queira sair.")
                
                elif data == "LEFT":
                    print("Você saiu do modo privado")
                
                elif data == "USER_LEFT":
                    print("Usuário não está mais online, voltando ao modo grupo.")
        
        except Exception as e:
            print(f"Um erro ocorreu: {e}")
            client.close()
            break

def write(client: socket.socket):
    while True:
        try:
            message = input()
            
            sendEncodeMsg(client, message)
        except EOFError:
            print("Mensagem inválida.")
        except OSError:
            print("Não foi possível enviar mensagem.")
            break

# Inicializar thread de recebimento
thread_rcv = threading.Thread(target=receive, args=(client,))
thread_rcv.start()
