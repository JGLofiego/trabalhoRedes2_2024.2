import random

'''
Calcula o totiente de um número primo
'''
def totiente(numero): 
    if eh_primo(numero):
        return numero - 1
    else:
        return False

    
'''
Verifica se um número gerado é primo
'''
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


'''
Gera um número aleatório E, satisfazendo as condições
'''
def gerar_E(num): 
    def mdc(n1, n2):
        while n2 != 0:
            resto = n1 % n2
            n1 = n2
            n2 = resto
        return n1

    while True:
        e = random.randrange(2, num) 
        if mdc(num, e) == 1:
            return e

        
'''
Gera um número primo aleatório
'''
def gerar_primo(): 
    while True: 
        x = random.randrange(1, 100) 
        if eh_primo(x):
            return x


'''
Função modular entre dois números
'''
def mod(a, b): 
    return a if a < b else a % b

    
'''
Cifra um texto
'''
def cifrar_texto(texto, e, n): 
    lista_cifrada = []
    for letra in texto:
        valor_letra = ord(letra)
        valor_cifrado = mod(valor_letra ** e, n)
        lista_cifrada.append(valor_cifrado)
    return lista_cifrada


'''
Descriptografa um texto cifrado
'''
def decifrar_texto(cifrado, n, d):
    lista_decifrada = []
    for valor_cifrado in cifrado:
        valor_original = mod(valor_cifrado ** d, n)
        letra = chr(valor_original)
        lista_decifrada.append(letra)
    return lista_decifrada


'''
Calcula a chave privada
'''
def calcular_chave_privada(toti, e):
    d = 0
    while mod(d * e, toti) != 1:
        d += 1
    return d


# Função para gerar chaves públicas e privadas
# def gerar_chave_publica_e_privada():
if __name__=='__main__':
    mensagem = "EU N SEI"
    p = gerar_primo() 
    q = gerar_primo() 
    n = p * q 
    totiente_N = totiente(p) * totiente(q)  
    e = gerar_E(totiente_N) 
    chave_publica = (n, e)
    d = calcular_chave_privada(totiente_N, e)
    # return chave_publica, d
    
    print('Sua chave pública:', chave_publica)
    mensagem_cifrada = cifrar_texto(mensagem, e, n)
    print('Sua mensagem cifrada:', mensagem_cifrada)
    print('Sua chave privada é:', d)
    mensagem_original = decifrar_texto(mensagem_cifrada, n, d)
    print('Sua mensagem original:', ''.join(mensagem_original))
