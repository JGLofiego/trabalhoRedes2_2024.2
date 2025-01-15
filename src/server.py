import socket
import threading
import os
from crypto import criptografar, descriptografar, sendEncodeMsg

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

client_list: list[socket.socket] = []
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

def broadcast(message: str, sender: socket.socket | None = None):
    for client in client_list:
        if client != sender:
            try:
                sendEncodeMsg(client, message)
            except Exception as e:
                print(f"Erro ao enviar mensagem para o cliente {client.getpeername()}: {e}")

def handle(client: socket.socket):    
    private = None
    
    addr = client.getpeername()
    n=0
    while True:
        try:
            data = client.recv(1024).decode("ascii")
            print(f"mensagem recebida de {addr}:", data)
            
            message = descriptografar(data)
            
            if message.startswith("/file"):
                n = n + 1
                message, filesize, name = message.split(", ", 2)
                name = os.path.basename(name)
                print(f"Recebendo arquivo {name}.")
                filename = f"../arquivos_testes/recebidos/{addr[1]}_{n}_{name}"
                with open(filename, "wb") as f:
                    filesize = int(filesize)
                    print(f"Fazendo download do arquivo {addr[1]}_{n}_{name} ...")
                    while filesize>0:
                        bytes_read = client.recv(1024)
                        f.write(bytes_read)
                        filesize = filesize-1024
                    print("Download concluido com sucesso.")
                continue
    
            if message.startswith("/join"):
                parts = message.split(" ", 1)
                
                if len(parts) < 2:
                    sendEncodeMsg(client, "INVALID")
                    print(f"Requisição de /join inválida por {addr}")
                    continue
                
                index = usernames.index(parts[1])
                private = client_list[index]
                
                sendEncodeMsg(client, f"JOINED {parts[1]}")
                print(f"{addr} entrou em chat privado com {private.getpeername()}")
            elif message.startswith("/leave"):
                private = None
                sendEncodeMsg(client, "LEFT")
                print(f"{addr} saiu do modo privado")
            else:
                if not private:
                    name = usernames[client_list.index(client)]
                    broadcast(f"{name}: {message}", client)
                else:
                    try:
                        index_client = client_list.index(client)
                        sendEncodeMsg(private, f"{usernames[index_client]} >> {message}")
                    except OSError:
                        sendEncodeMsg(client, "USER_LEFT")
                        private = None
                        continue
        except ValueError:
            sendEncodeMsg(client, "USER_NOT_FOUND")
            print("Usuário do /join não encontrado.")
            continue
        except:
            client.close()
            index = client_list.index(client)
            client_list.remove(client)
            print(f"Conexão removida: {addr}")
            broadcast(f"{usernames[index]} saiu do chat.")
            usernames.pop(index)
            break

def authenticate(client: socket.socket):
    while True:
        addr = client.getpeername()
        
        sendEncodeMsg(client, "REGISTER_OR_LOGIN")
        print(f"Requisitando escolha de autenticação de {addr}")
        choice = client.recv(1024).decode("ascii")
        
        choice = descriptografar(choice)

        if choice == "REGISTER":
            print(f"Registro escolhido por {addr}")
            
            print(f"Requisitando username de {addr}")
            sendEncodeMsg(client, "USERNAME")
            
            username = client.recv(1024).decode("ascii")
            print(f"Usuario recebido de {addr}: {username}")
            
            username = descriptografar(username)

            if username in users:
                print(f"Usuário {username} já existe.")
                sendEncodeMsg(client, "USER_EXISTS")
                continue

            print(f"Requisitando senha de {addr}")
            sendEncodeMsg(client, "PASSWORD")
            password = client.recv(1024).decode("ascii")
            print(f"Senha recebida de {addr}")
            
            password = descriptografar(password)

            users[username] = password
            save_user(username, password)
            
            print(f"Usuário {username} registrado com sucesso em {addr}.")
            sendEncodeMsg(client, "REGISTER_SUCCESS")
            return username

        elif choice == "LOGIN":
            print(f"Login escolhido por {addr}")
            
            print(f"Requisitando username de {addr}")
            sendEncodeMsg(client, "USERNAME")
            username = client.recv(1024).decode("ascii")
            print(f"Usuario recebido de {addr}: {username}")
            
            username = descriptografar(username)

            if username not in users:
                print(f"Usuário {username} não encontrado.")
                sendEncodeMsg(client, "USER_NOT_FOUND")
                continue

            print(f"Requisitando senha de {addr}")
            sendEncodeMsg(client, "PASSWORD")
            password = client.recv(1024).decode("ascii")
            print(f"Senha recebida de {addr}")
            
            password = descriptografar(password)

            if users[username] != password:
                print(f"Senha incorreta para o usuário {username}.")
                sendEncodeMsg(client, "INVALID_PASSWORD")
                continue

            print(f"Usuário {username} logado com sucesso em {addr}.")
            sendEncodeMsg(client, "LOGIN_SUCCESS")
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

def read_file(client: socket.socket):
    print("Recebendo arquivo.")
    with open("r_teste.txt", "wb") as f:
        while True:
            print("Recebendo arquivo.")
            bytes_read = client.recv(1024)
            if not bytes_read:    
                print("Arquivo recebido.")
                break
            f.write(bytes_read)

for i in range(MAX_USERS):
    thread = threading.Thread(target=receive)
    thread.start()