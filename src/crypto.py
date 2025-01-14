import random
import math
import base64
import json
from sympy import randprime

def totiente(p, q):
    return (p - 1) * (q - 1)

def gerar_E(totiente_n):
    while True:
        e = random.randrange(2, totiente_n)
        if math.gcd(totiente_n, e) == 1:
            return e
        
def gerar_primo():
    return randprime(2**30, 2**31)  # Maior intervalo de números primos

def cifrar_texto(mensagem, e, n):
    mensagem_cifrada = []
    for char in mensagem:
        num_cifrado = pow(ord(char), e, n)
        if num_cifrado > n:  # Garantir que o número cifrado esteja dentro do intervalo de n
            raise ValueError(f"Valor cifrado fora do intervalo permitido: {num_cifrado}")
        mensagem_cifrada.append(num_cifrado)
    return mensagem_cifrada


def decifrar_texto(mensagem_cifrada, d, n):
    mensagem_decifrada = []
    for char in mensagem_cifrada:
        decifrado = pow(char, d, n)
        if decifrado > 0x10FFFF:  # Garantir que o valor está no intervalo Unicode válido
            decifrado = decifrado % 0x110000
        mensagem_decifrada.append(chr(decifrado))
    return ''.join(mensagem_decifrada)


def calcular_chave_privada(toti, e):
    return pow(e, -1, toti)

def gerar_chave_publica_e_privada():
    p = gerar_primo()
    q = gerar_primo()
    n = p * q
    print(f"Valor de n: {n}")
    totiente_n = totiente(p, q)
    e = gerar_E(totiente_n)
    d = calcular_chave_privada(totiente_n, e)
    return (n, e), d

def split_into_chunks(value, chunk_size=4):
    value_str = str(value)
    return [int(value_str[i:i+chunk_size]) for i in range(0, len(value_str), chunk_size)]

def reassemble_from_chunks(chunks):
    return int(''.join(str(chunk) for chunk in chunks))

def encode_message(mensagem_cifrada):
    chunks = [split_into_chunks(value) for value in mensagem_cifrada]
    mensagem_bytes = json.dumps(chunks).encode("utf-8")
    return base64.b64encode(mensagem_bytes).decode("utf-8")

def decode_message(mensagem_cifrada_str):
    mensagem_bytes = base64.b64decode(mensagem_cifrada_str.encode("utf-8"))
    chunks = json.loads(mensagem_bytes.decode("utf-8"))
    return [reassemble_from_chunks(chunk) for chunk in chunks]
