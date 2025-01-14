import socket, threading, time
from crypto import criptografar, descriptografar

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
    while True:
        try:
            # Receber a mensagem criptografada e descriptografá-la
            data = client.recv(2048).decode("ascii")
            if "|" in data:
                iv_str, mensagem_criptografada = data.split('|')
                iv = [int(x) for x in iv_str.split(',')]
                mensagem_criptografada = [int(b) for b in mensagem_criptografada.strip('[]').split(',')]
                mensagem = descriptografar(iv, mensagem_criptografada)
            else:
                if data == "REGISTER_OR_LOGIN":
                    choice = input("Digite 'REGISTER' para cadastrar ou 'LOGIN' para logar: ")
                    client.send(choice.encode("ascii"))
                    
                elif data == "USERNAME":
                    username = input("Digite o nome de usuário: ")
                    client.send(username.encode("ascii"))
                    
                elif data == "PASSWORD":
                    password = input("Digite a senha: ")
                    client.send(password.encode("ascii"))
                    
                elif data == "USER_EXISTS":
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
            mensagem = input("Digite sua mensagem: ")
            
            iv, mensagem_criptografada = criptografar(mensagem)
            
            iv_str = ','.join([str(x) for x in iv])
            client.send(f"{iv_str}|{mensagem_criptografada}".encode("ascii"))
        except Exception as e:
            print(f"Não foi possível enviar mensagem: {e}")
            break

# Inicializar thread de recebimento
thread_rcv = threading.Thread(target=receive, args=(client,))
thread_rcv.start()
