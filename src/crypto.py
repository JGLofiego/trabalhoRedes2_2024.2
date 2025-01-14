import aes
import aes.utils as utils
import socket

# Chave mestre de 256 bits (32 bytes)
mk = 0x000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f

# Inicializa o AES 
cipher = aes.aes(mk, 256, mode='CTR', padding='PKCS#7')

def sendEncodeMsg(client: socket.socket, message: str):
    code_message = criptografar(message)
    client.send(code_message.encode("ascii"))

# Função para criptografar uma mensagem
def criptografar(mensagem: str):
    mensagem_bytes = list(mensagem.encode('ascii'))
    
    mensagem_criptografada = cipher.enc(mensagem_bytes)
    
    iv = cipher.iv
                
    iv_str = ','.join([str(x) for x in iv])
    
    return f"{iv_str}|{mensagem_criptografada}"

# Função para descriptografar uma mensagem
def descriptografar(data: str):
    
    if(len(data.split("|")) < 2):
        raise ConnectionAbortedError
    
    iv_str, mensagem_criptografada = data.split('|')
    iv = [int(x) for x in iv_str.split(',')]
    mensagem_criptografada = [int(b) for b in mensagem_criptografada.strip('[]').split(',')]
    
    cipher_dec = aes.aes(mk, 256, mode='CTR', padding='PKCS#7', iv=iv)
    
    mensagem_descriptografada = cipher_dec.dec(mensagem_criptografada)
    
    return bytes(mensagem_descriptografada).decode('ascii')

# Exemplo de uso das funções
# if __name__ == "__main__":
#     mensagem = "Teste de criptografia AES"
#     print(f"Mensagem original: {mensagem}")
    
#     iv, criptografada = criptografar(mensagem)
#     print(f"Mensagem criptografada: {criptografada}")
    
#     descriptografada = descriptografar(iv, criptografada)
#     print(f"Mensagem descriptografada: {descriptografada}")