from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey
from cryptography.hazmat.primitives.ciphers import algorithms, modes, Cipher

from repository.config.settings import settings


def encrypt_symmetric(data: bytes, key: bytes) -> bytes:
    algorithm = algorithms.AES(key)
    mode = modes.CTR(settings.INITIALIZATION_VECTOR)
    encryptor = Cipher(algorithm, mode).encryptor()

    return encryptor.update(data) + encryptor.finalize()


def encrypt_asymmetric(data: bytes, public_key: RSAPublicKey) -> bytes:
    return public_key.encrypt(data, padding.PKCS1v15())


def decrypt_symmetric(data: bytes, key: bytes) -> bytes:
    algorithm = algorithms.AES(key)
    mode = modes.CTR(settings.INITIALIZATION_VECTOR)
    decryptor = Cipher(algorithm, mode).decryptor()

    return decryptor.update(data) + decryptor.finalize()


def decrypt_asymmetric(data: bytes, private_key: RSAPrivateKey) -> bytes:
    return private_key.decrypt(data, padding.PKCS1v15())
