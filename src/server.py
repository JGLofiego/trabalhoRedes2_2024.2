import socket
import threading
import os

HOST = "127.0.0.1"
PORT = 3000

# Cria o socket do servidor
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_address = (HOST, PORT)
sock.bind(server_address)
sock.listen()
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

def broadcast(message: str):
    for client in client_list:
        client.send(message.encode("ascii"))

def handle(client: socket.socket):
    while True:
        try:
            message = client.recv(1024).decode("ascii")
            print(f"mensagem recebida de {client.getpeername()}:", message)
            broadcast(message)
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
        client.send("REGISTER_OR_LOGIN".encode("ascii"))
        choice = client.recv(1024).decode("ascii")

        if choice == "REGISTER":
            client.send("USERNAME".encode("ascii"))
            username = client.recv(1024).decode("ascii")

            if username in users:
                client.send("USER_EXISTS".encode("ascii"))
                continue

            client.send("PASSWORD".encode("ascii"))
            password = client.recv(1024).decode("ascii")

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
        client, address = sock.accept()
        print(f"Conexão estabelecida: {address}")

        username = authenticate(client)
        client_list.append(client)
        usernames.append(username)

        broadcast(f"{username} se juntou ao chat!")

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

receive()
