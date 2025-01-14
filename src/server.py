import socket
import threading
import os
from crypto import gerar_chave_publica_e_privada, decifrar_texto, decode_message

HOST = "localhost"
PORT = 3000
MAX_USERS = 5

public_key, private_key = gerar_chave_publica_e_privada()
n, e = public_key

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_address = (HOST, PORT)
sock.bind(server_address)
sock.listen(MAX_USERS)
print(f"Iniciando o servidor no host {server_address[0]} com a porta {server_address[1]}")

client_list = []
usernames = []
users = {}

if os.path.exists("users.txt"):
    with open("users.txt", "r") as f:
        for line in f:
            username, password = line.strip().split(",")
            users[username] = password

def save_user(username, password):
    with open("users.txt", "a") as f:
        f.write(f"{username},{password}\n")

def broadcast(message: str, sender: socket.socket):
    for client in client_list:
        if client != sender:
            try:
                client.send(message.encode("utf-8"))
            except Exception as e:
                print(f"Erro ao enviar mensagem para o cliente {client.getpeername()}: {e}")

def handle(client: socket.socket):
    # Enviar a chave pública para o cliente
    client.send(f"{n},{e}".encode("utf-8"))

    while True:
        try:
            encrypted_message_str = client.recv(1024).decode("utf-8")
            if not encrypted_message_str:
                raise ConnectionResetError
            encrypted_message = decode_message(encrypted_message_str)
            print(f"Mensagem cifrada recebida de {client.getpeername()}: {encrypted_message}")
            message = decifrar_texto(encrypted_message, private_key, n)
            print(f"Mensagem decifrada de {client.getpeername()}: {message}")
            broadcast(message, client)
        except Exception as ex:
            print(f"Erro ao lidar com a mensagem: {ex}")
            break


def authenticate(client: socket.socket):
    while True:
        addr = client.getpeername()
        
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
        
        try:
            username = authenticate(client)
        except:
            client.close()
            continue
        
        client_list.append(client)
        usernames.append(username)

        broadcast(f"{username} se juntou ao chat!", client)

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

for _ in range(MAX_USERS):
    thread = threading.Thread(target=receive)
    thread.start()
