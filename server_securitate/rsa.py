from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
import binascii
from urllib.parse import unquote

def rsa_decrypt(payload):
    payload = bytes(payload, 'utf-8')
    payload = binascii.unhexlify(payload)
    
    file_out = open('/tmp/abc', 'wb')
    file_out.write(payload)
    file_out.close()

    private_key = RSA.import_key(open("rsa_key.pem").read())
    file_in = open("/tmp/abc", "rb")
    
    enc_session_key, nonce, tag, ciphertext = \
    [ file_in.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1) ]
    file_in.close()

    # Decrypt the session key with the private RSA key
    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)

    # Decrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    data = cipher_aes.decrypt_and_verify(ciphertext, tag)
    data = data.decode('utf-8')
    return data
    
    
def rsa_decrypt_raw(payload):
    
    file_out = open('/tmp/abc', 'wb')
    file_out.write(payload)
    file_out.close()

    private_key = RSA.import_key(open("rsa_key.pem").read())
    file_in = open("/tmp/abc", "rb")
    
    enc_session_key, nonce, tag, ciphertext = \
    [ file_in.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1) ]
    file_in.close()

    # Decrypt the session key with the private RSA key
    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)

    # Decrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    data = cipher_aes.decrypt_and_verify(ciphertext, tag)
    return data
    
def request_get(data, val):
    i1 = data.find(val+'=')
    if i1 == -1:
        return ""
    i2 = data.find('&', i1)
    if i2 == -1:
        i2 = len(data)
    i1 = i1+len(val)+1
    s = data[i1:i2]
    #print(s)
    return unquote(s)
