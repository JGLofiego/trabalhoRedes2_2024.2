import socket
import threading
import os
from crypto import criptografar, descriptografar

HOST = "localhost"
PORT = 3000
MAX_USERS = 5

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

def sendEncodeMsg(client: socket.socket, message: str):
    code_message = criptografar(message)
    client.send()

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

def broadcast(message: str, sender: socket.socket | None = None):
    for client in client_list:
        if client != sender:
            try:
                client.send(message.encode("utf-8"))
            except Exception as e:
                print(f"Erro ao enviar mensagem para o cliente {client.getpeername()}: {e}")

def handle(client: socket.socket):    
    private = None
    
    while True:
        try:
            data = client.recv(1024).decode("ascii")
            print(f"mensagem recebida de {client.getpeername()}:", data)
            
            message = descriptografar(data)
            
            if message.startswith("/join"):
                parts = message.split(" ", 1)
                
                if len(parts) < 2:
                    client.send("INVALID".encode("ascii"))
                    continue
                
                index = usernames.index(parts[1])
                private = client_list[index]
                
                
                client.send(f"JOINED {parts[1]}".encode("ascii"))
            elif message.startswith("/leave"):
                private = None
                client.send("LEFT".encode("ascii"))
            else:
                if not private:
                    name = usernames[client_list.index(client)]
                    broadcast(f"{name}: {message}", client)
                else:
                    try:
                        index_client = client_list.index(client)
                        private.send(f"{usernames[index_client]} >> {message}".encode("ascii"))
                    except OSError:
                        client.send("USER_LEFT".encode("ascii"))
                        private = None
                        continue
        except ValueError:
            client.send("USER_NOT_FOUND".encode("ascii"))
            continue
        except:
            index = client_list.index(client)
            client_list.remove(client)
            print(f"Conexão removida: {client.getpeername()}")
            client.close()
            broadcast(f"{usernames[index]} saiu do chat.")
            usernames.pop(index)
            break

def authenticate(client: socket.socket):
    while True:
        addr = client.getpeername()
        
        client.send("REGISTER_OR_LOGIN".encode("ascii"))
        print(f"Requisitando escolha de autenticação de {addr}")
        choice = client.recv(1024).decode("ascii")

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

        broadcast(f"{username} se juntou ao chat!")

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

for i in range(MAX_USERS):
    thread = threading.Thread(target=receive)
    thread.start()