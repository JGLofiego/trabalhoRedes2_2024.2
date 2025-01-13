import random
import math

def totiente(numero): 
    if eh_primo(numero):
        return numero - 1
    else:
        return False

def eh_primo(n): 
    if n <= 1:
        return False
    if n <= 3:
        return True

    if n % 2 == 0 or n % 3 == 0:
        return False

    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def gerar_E(num): 
    while True:
        e = random.randrange(2, num) 
        if math.gcd(num, e) == 1: 
            return e
 

def gerar_primo(): 
    while True: 
        x = random.randrange(1, 100) 
        if eh_primo(x):
            return x

def cifrar_texto(texto, e, n): 
    lista_cifrada = []
    for letra in texto:
        valor_letra = ord(letra)
        valor_cifrado = pow(valor_letra, e, n)  
        lista_cifrada.append(valor_cifrado)
    return lista_cifrada


def decifrar_texto(cifrado, n, d):
    lista_decifrada = []
    for valor_cifrado in cifrado:
        valor_original = pow(valor_cifrado, d, n) 
        letra = chr(valor_original)
        lista_decifrada.append(letra)
    return lista_decifrada


def calcular_chave_privada(toti, e):
    return pow(e, -1, toti)  



def gerar_chave_publica_e_privada():
    p = gerar_primo() 
    q = gerar_primo() 
    n = p * q 
    totiente_N = totiente(p) * totiente(q)  
    e = gerar_E(totiente_N) 
    chave_publica = (n, e)
    d = calcular_chave_privada(totiente_N, e)
    return chave_publica, d
