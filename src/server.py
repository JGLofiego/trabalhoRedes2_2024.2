import socket
import threading
import os
from crypto import gerar_chave_publica_e_privada, decifrar_texto, cifrar_texto

HOST = "localhost"
PORT = 3000
MAX_USERS = 5

# Gera chaves para criptografia
public_key, private_key = gerar_chave_publica_e_privada()
n, e = public_key
# print(f"Chave pública: {public_key}")
# print(f"Chave privada: {private_key}")
# print(f"n: {n}")
# print(f"e: {e}")

# Cria o socket do servidor
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_address = (HOST, PORT)
sock.bind(server_address)
sock.listen(MAX_USERS)
print(f"Iniciando o server no host {server_address[0]} com a porta {server_address[1]}")

client_list = []
usernames = []
users = {}  # Armazena usernames e senhas

# Carrega usuários do arquivo (se existir)
if os.path.exists("users.txt"):
    with open("users.txt", "r") as f:
        for line in f:
            username, password = line.strip().split(",")
            users[username] = password

def save_user(username, password):
    """Salva um novo usuário no arquivo."""
    with open("users.txt", "a") as f:
        f.write(f"{username},{password}\n")

def broadcast(message: str, sender: socket.socket, n, e):
    encrypted_message = cifrar_texto(message, e, n)
    # print(f"Mensagem cifrada: {encrypted_message}")
    for client in client_list:
        if client != sender:  
            try:
                client.send(str(encrypted_message).encode("ascii"))
            except Exception as e:
                print(f"Erro ao enviar mensagem para o cliente {client.getpeername()}: {e}")


def handle(client: socket.socket):
    while True:
        try:
            message  = client.recv(1024).decode("ascii")
            # message = decifrar_texto(eval(encrypted_message), n, private_key)
            print(f"mensagem recebida de {client.getpeername()}:", message)
            broadcast(message, client, n, e)
        except:
            index = client_list.index(client)
            client_list.remove(client)
            print(f"Conexão removida: {client.getpeername()}")
            client.close()
            broadcast(f"{usernames[index]} saiu do chat.", None, n, e)
            usernames.pop(index)
            break

def authenticate(client: socket.socket):
    while True:
        addr = client.getpeername()
        
        client.send("REGISTER_OR_LOGIN".encode("ascii"))
        print(f"Requisitando escolha de autenticação de {addr}")
        choice = client.recv(1024).decode("ascii")
        print(f"Escolha recebida do cliente: {choice}")


        if choice == "REGISTER":
            print(f"Registro escolhido por {addr}")
            
            print(f"Requisitando username de {addr}")
            client.send("USERNAME".encode("ascii"))
            
            username = client.recv(1024).decode("ascii")
            print(f"Usuario recebido de {addr}: {username}")

            if username in users:
                print(f"Usuário {username} já existe.")
                client.send("USER_EXISTS".encode("ascii"))
                continue

            print(f"Requisitando senha de {addr}")
            client.send("PASSWORD".encode("ascii"))
            password = client.recv(1024).decode("ascii")
            print(f"Senha recebida de {addr}")

            users[username] = password
            save_user(username, password)
            
            print(f"Usuário {username} registrado com sucesso em {addr}.")
            client.send("REGISTER_SUCCESS".encode("ascii"))
            return username

        elif choice == "LOGIN":
            print(f"Login escolhido por {addr}")
            
            print(f"Requisitando username de {addr}")
            client.send("USERNAME".encode("ascii"))
            username = client.recv(1024).decode("ascii")
            print(f"Usuario recebido de {addr}: {username}")

            if username not in users:
                print(f"Usuário {username} não encontrado.")
                client.send("USER_NOT_FOUND".encode("ascii"))
                continue

            print(f"Requisitando senha de {addr}")
            client.send("PASSWORD".encode("ascii"))
            password = client.recv(1024).decode("ascii")
            print(f"Senha recebida de {addr}")

            if users[username] != password:
                print(f"Senha incorreta para o usuário {username}.")
                client.send("INVALID_PASSWORD".encode("ascii"))
                continue

            print(f"Usuário {username} logado com sucesso em {addr}.")
            client.send("LOGIN_SUCCESS".encode("ascii"))
            return username

def receive():
    while True:
        try:
            client, address = sock.accept()
            print(f"Conexão estabelecida: {address}")
        except:
            print("Conexão falhou.")
            client.close()
            continue
        
        try:
            username = authenticate(client)
        except:
            print(f"Erro de autenticação da conexão {client.getpeername()}.")
            print(f"Removendo conexão {client.getpeername()}.")
            client.close()
            continue
        
        client_list.append(client)
        usernames.append(username)

        broadcast(f"{username} se juntou ao chat!", client, n, e)  # Não envie para o remetente

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

for i in range(MAX_USERS):
    thread = threading.Thread(target=receive)
    thread.start()