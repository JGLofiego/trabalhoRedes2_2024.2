import socket
import threading

HOST = "127.0.0.1"
PORT = 3000

username = input("Digite o seu usuário: ")

# Faz a conexão com o socket do servidor
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

print("Conexão estabelecida!")

print(f"{username} entrou no chat.")

# Função que lida com recebimento de mensagens do servidor
def receive():
    while True:
        try:
            message = client.recv(1024).decode("ascii")
            
            # Se a mensagem vinda do servidor for USERNAME, envia o usuário para o servidor
            if message == "USERNAME":
                client.send(username.encode("ascii"))
                
            # Se a mensagem vinda do servidor for USERS, é a lista de usuários conectados
            elif message.startswith("USERS"):
                users = message[6:]
                if users == "":
                    print("Ninguém além de você no chat :(")
                    continue
                print(f"Usuários no chat: {message[6:]}")
            else:
                print(message)
        except:
            print("Um erro ocorreu!")
            client.close()
            break

# Função que lida com mandar mensagens pro servidor
def write():
    input_message = input() 
    message = f"{username}: {input_message}"
    client.send(message.encode("ascii"))

# Inicia a thread que lida com recebimento de mensagens
thread_rcv = threading.Thread(target=receive)
thread_rcv.start()

# Inicia a thread que lida com envio de mensagens
thread_wrt = threading.Thread(target=write)
thread_wrt.start()