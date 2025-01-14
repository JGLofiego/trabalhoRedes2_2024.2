import socket, threading
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
        
def broadcast(message, sender: socket.socket | None = None):
    for client in client_list:
        if client != sender:
            try:
                # Criptografar a mensagem antes de enviar
                iv, mensagem_criptografada = criptografar(message)
                iv_str = ','.join([str(x) for x in iv])
                client.send(f"{iv_str}|{mensagem_criptografada}".encode("ascii"))
            except:
                client_list.remove(client)

def authenticate(client: socket.socket):
    while True:
        addr = client.getpeername()
        
        # Requisitar autenticação sem criptografia
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
        else:
            client.send("INVALID_CHOICE".encode("ascii"))

def handle(client: socket.socket):
    username = authenticate(client)
    if username:
        client_list.append(client)
        broadcast(f"{username} se juntou ao chat!")

        while True:
            try:
                # Receber a mensagem criptografada e descriptografá-la
                data = client.recv(2048).decode("ascii")
                if "|" in data:
                    iv_str, mensagem_criptografada = data.split('|')
                    iv = [int(x) for x in iv_str.split(',')]
                    mensagem_criptografada = [int(b) for b in mensagem_criptografada.strip('[]').split(',')]
                    mensagem = descriptografar(iv, mensagem_criptografada)
                    print(f"mensagem recebida de {client.getpeername()}:", mensagem)
                    broadcast(mensagem)
            except:
                client_list.remove(client)
                client.close()
                break

def receive():
    while True:
        try:
            client, address = sock.accept()
            print(f"Conexão estabelecida: {address}")
            thread = threading.Thread(target=handle, args=(client,))
            thread.start()
        except Exception as e:
            print(f"Erro ao aceitar conexão: {e}")

receive()
