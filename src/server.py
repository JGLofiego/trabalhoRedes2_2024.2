import socket
import threading
import os
from crypto import gerar_chave_publica_e_privada, decifrar_texto, cifrar_texto

HOST = "127.0.0.1"
PORT = 3000
MAX_USERS = 5

# Gera chaves para criptografia
public_key, private_key = gerar_chave_publica_e_privada()
n, e = public_key
print(f"Chave pública: {public_key}")
print(f"Chave privada: {private_key}")
print(f"n: {n}")
print(f"e: {e}")

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

def broadcast(message: str, sender: socket.socket):
    public_key, private_key = gerar_chave_publica_e_privada()
    n, e = public_key

    encrypted_message = cifrar_texto(message, e, n)
    print(f"Mensagem cifrada: {encrypted_message}")
    for client in client_list:
        if client != sender:  
            try:
                client.send(str(encrypted_message).encode("ascii"))
            except Exception as e:
                print(f"Erro ao enviar mensagem para o cliente {client.getpeername()}: {e}")


def handle(client: socket.socket):
    while True:
        try:
            message = client.recv(1024).decode("ascii")
            print(f"mensagem recebida de {client.getpeername()}:", message)
            broadcast(message, client)
        except:
            index = client_list.index(client)
            client_list.remove(client)
            print(f"Conexão removida: {client.getpeername()}")
            client.close()
            broadcast(f"{usernames[index]} saiu do chat.", None)
            usernames.pop(index)
            break

def authenticate(client: socket.socket):
    while True:
        client.send("REGISTER_OR_LOGIN".encode("ascii"))
        choice = client.recv(1024).decode("ascii")
        print(f"Escolha recebida do cliente: {choice}")


        if choice == "REGISTER":
            client.send("USERNAME".encode("ascii"))
            username = client.recv(1024).decode("ascii")
            print(f"Username para registro: {username}")
            
            if username in users:
                client.send("USER_EXISTS".encode("ascii"))
                continue

            client.send("PASSWORD".encode("ascii"))
            password = client.recv(1024).decode("ascii")
            print(f"Senha para registro: {password}")

            users[username] = password
            save_user(username, password)
            client.send("REGISTER_SUCCESS".encode("ascii"))
            return username

        elif choice == "LOGIN":
            client.send("USERNAME".encode("ascii"))
            username = client.recv(1024).decode("ascii")

            if username not in users:
                client.send("USER_NOT_FOUND".encode("ascii"))
                continue

            client.send("PASSWORD".encode("ascii"))
            password = client.recv(1024).decode("ascii")

            if users[username] != password:
                client.send("INVALID_PASSWORD".encode("ascii"))
                continue

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

        broadcast(f"{username} se juntou ao chat!", client)  # Não envie para o remetente

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

for i in range(MAX_USERS):
    thread = threading.Thread(target=receive)
    thread.start()