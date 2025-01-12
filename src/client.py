import socket
import threading
from crypto import gerar_chave_publica_e_privada, decifrar_texto, cifrar_texto

HOST = "127.0.0.1"
PORT = 3000

# Gera chaves para criptografia
public_key, private_key = gerar_chave_publica_e_privada()
n, e = public_key
# print(f"Chave pública: {public_key}")
# print(f"Chave privada: {private_key}")
# print(f"n: {n}")
# print(f"e: {e}")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

print("Conexão estabelecida!")

def receive():
    while True:
        try:
            message = client.recv(1024).decode("ascii")

            if message == "REGISTER_OR_LOGIN":
                choice = input("Digite 'REGISTER' para cadastrar ou 'LOGIN' para logar: ")
                client.send(choice.encode("ascii"))

            elif message == "USERNAME":
                username = input("Digite o nome de usuário: ")
                client.send(username.encode("ascii"))

            elif message == "PASSWORD":
                password = input("Digite a senha: ")
                client.send(password.encode("ascii"))

            elif message == "USER_EXISTS":
                print("Usuário já existe. Tente novamente.")

            elif message == "REGISTER_SUCCESS":
                print("Cadastro realizado com sucesso!")
                thread_wrt = threading.Thread(target=write)
                thread_wrt.start()

            elif message == "USER_NOT_FOUND":
                print("Usuário não encontrado. Tente novamente.")

            elif message == "INVALID_PASSWORD":
                print("Senha incorreta. Tente novamente.")

            elif message == "LOGIN_SUCCESS":
                print("Login realizado com sucesso!")
                thread_wrt = threading.Thread(target=write)
                thread_wrt.start()

            else:
                print(message)
        except:
            print("Um erro ocorreu!")
            client.close()
            break

def write():
    while True:
        try:
            message = input()
            client.send(message.encode("ascii"))
        except:
            print("Erro ao enviar mensagem.")
            client.close()
            break

thread_rcv = threading.Thread(target=receive)
thread_rcv.start()
