import socket
import threading

HOST = "127.0.0.1"
PORT = 3000
# Cria o socket do servidor, recebe como parâmetro família do socket e tipo de socket
# AF_INET - Constante representando que a família de endereço é do tipo internet
# SOCK_STREAM - Constante representando que o socket é do tipo TCP
sock = socket.socket(socket.AF_INET,  socket.SOCK_STREAM)

# Otimizador de socket para utilizar o mesmo endereço.
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Vincula o socket ao endereço e a porta
server_address = (HOST, PORT)
sock.bind(server_address)

# Função para o socket ouvir as possíveis conexões
sock.listen()
print (f"Iniciando o server no host {server_address[0]} com a porta {server_address[1]}")

client_list: list[socket.socket] = []
usernames = []

# Função de enviar mensagem para todas as conexões
def broadcast(message: str):
    for client in client_list:
        client.send(message)

# Função de lidar com o cliente
def handle(client: socket.socket):
    while True:
        # Tenta receber uma mensagem do cliente, se ocorrer um erro significa que a conexão com o cliente foi perdida ou fechada.
        try:
            message = client.recv(1024)
            broadcast(message)
        # Removendo a conexão que causou o erro.
        except:
            index = client_list.index(client)
            client_list.remove(client)
            print(f"Conexão removida: {client.getpeername()}")
            client.close()
            broadcast(f"{usernames[index]} saiu do chat.".encode("ascii"))
            usernames.remove(usernames[index])
            break

# Função para receber uma nova conexão.
def receive():    
    while True:
        # Só aceita o cliente, sem autenticação.
        client, address = sock.accept()
        print(f"Conexão estabelecida: {address}")
        
        # Manda uma mensagem para o cliente pedindo o usuário
        client.send("USERNAME".encode("ascii"))
        
        # Recebe a primeira resposta do cliente, ou seja, o usuário
        username = client.recv(1024).decode("ascii")
        
        # Manda uma mensagem para o cliente com todos os usuários presentes
        client.send(("USERS " + ", ".join(usernames)).encode("ascii"))
        
        print(f"Usuario: {username}")
        broadcast(f"{username} se juntou ao chat!".encode("ascii"))
        
        client_list.append(client)
        usernames.append(username)
        
        # Ao conectar o usuário, cria uma thread para o cliente
        # Cada thread é responsável por receber as mensagens daquele cliente específico
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

receive()
        

        