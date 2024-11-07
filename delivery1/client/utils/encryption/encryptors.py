import base64
import json
import os
from typing import Any

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives.ciphers import algorithms, modes, Cipher

from utils.repository_info import get_repository_public_key, get_repository_iv


def encrypt_symmetric(data: bytes, key: bytes, iv: bytes) -> bytes:
    algorithm = algorithms.AES(key)
    mode = modes.CTR(iv)
    encryptor = Cipher(algorithm, mode).encryptor()

    data = encryptor.update(data) + encryptor.finalize()
    return base64.encodebytes(data)


def encrypt_asymmetric(data: bytes, public_key: RSAPublicKey) -> bytes:
    data = public_key.encrypt(data, padding.PKCS1v15())
    return base64.encodebytes(data).replace(b"\n", b"\\n").replace(b"\r", b"\\r")


def encrypt_dict_repository(
    data: dict[str, Any] | None,
    public_key: RSAPublicKey = get_repository_public_key(),
    iv: bytes = get_repository_iv(),
) -> tuple[str, str | None]:
    """
    Encrypts a dictionary using a symmetric key and encrypts the symmetric key using an asymmetric key

    :param data: The dictionary to be encrypted
    :type data: dict[str, Any]
    :param public_key: The public key to encrypt the symmetric key
    :type public_key: RSAPublicKey
    :param iv: The initialization vector to be used in the symmetric encryption
    :type iv: bytes

    :return: A dictionary containing the encrypted data and the encrypted symmetric key
    :rtype: dict[str, str]
    """
    key = os.urandom(16)
    key_bytes = encrypt_asymmetric(key, public_key).decode()

    if data is None:
        return key_bytes, None

    data_bytes = json.dumps(data).encode()
    data_bytes = encrypt_symmetric(data_bytes, key, iv).decode()
    return key_bytes, data_bytes


def encrypt_dict_session(
    data: dict[str, Any] | None,
    session_file: bytes,
    public_key: RSAPublicKey = get_repository_public_key(),
    iv: bytes = get_repository_iv(),
) -> tuple[str, str | None]:
    key_bytes = encrypt_asymmetric(session_file, public_key).decode()

    if data is None:
        return key_bytes, None

    data_bytes = json.dumps(data).encode()
    data_bytes = encrypt_symmetric(data_bytes, key, iv).decode()
    return key_bytes, data_bytes


def decrypt_symmetric(data: bytes, key: bytes, iv: bytes) -> bytes:
    data = base64.decodebytes(data)
    algorithm = algorithms.AES(key)
    mode = modes.CTR(iv)
    decryptor = Cipher(algorithm, mode).decryptor()

    return decryptor.update(data) + decryptor.finalize()


def decrypt_asymmetric(data: bytes, private_key: RSAPrivateKey) -> bytes:
    data = base64.decodebytes(data)
    return private_key.decrypt(data, padding.PKCS1v15())
