from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey
from cryptography.hazmat.primitives.ciphers import algorithms, modes, Cipher


def encrypt_symmetric(data: bytes, key: bytes, iv: bytes) -> bytes:
    algorithm = algorithms.AES(key)
    mode = modes.CTR(iv)
    encryptor = Cipher(algorithm, mode).encryptor()

    return encryptor.update(data) + encryptor.finalize()


def encrypt_asymmetric(data: bytes, public_key: RSAPublicKey) -> bytes:
    return public_key.encrypt(data, padding.PKCS1v15())


def decrypt_symmetric(data: bytes, key: bytes, iv: bytes) -> bytes:
    algorithm = algorithms.AES(key)
    mode = modes.CTR(iv)
    decryptor = Cipher(algorithm, mode).decryptor()

    return decryptor.update(data) + decryptor.finalize()


def decrypt_asymmetric(data: bytes, private_key: RSAPrivateKey) -> bytes:
    return private_key.decrypt(data, padding.PKCS1v15())


# workaround com um switch case para escolher uma tonelada de algoritmos de encriptação
def encrypt_based_on_alg(data: bytes, key: bytes, iv: bytes, alg: str) -> bytes:
    match alg:
        # case "rsa":
        #     return encrypt_asymmetric(data, key)
        # case "aes":
        #     return encrypt_symmetric(data, key, iv)
        case _:
            return encrypt_symmetric(data, key, iv)
