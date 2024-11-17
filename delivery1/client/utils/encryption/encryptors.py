import base64
import json
import os
from typing import Any

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives.ciphers import algorithms, modes, Cipher

from utils.encoding import b64_encode_and_escape, b64_decode_and_unescape
from utils.repository_info import get_repository_public_key


def encrypt_symmetric(data: bytes, key: bytes, iv: bytes) -> bytes:
    algorithm = algorithms.AES(key)
    mode = modes.CTR(iv)
    encryptor = Cipher(algorithm, mode).encryptor()

    data = encryptor.update(data) + encryptor.finalize()
    return base64.encodebytes(data)


def encrypt_asymmetric(data: bytes, public_key: RSAPublicKey) -> bytes:
    return public_key.encrypt(data, padding.PKCS1v15())


def encrypt_key(
    key: bytes = os.urandom(32), public_key: RSAPublicKey = get_repository_public_key()
) -> str:
    return b64_encode_and_escape(encrypt_asymmetric(key, public_key))


def encrypt_request(
    data: dict[str, Any] | None,
    key: bytes = os.urandom(32),
    public_key: RSAPublicKey = get_repository_public_key(),
) -> tuple[str, str | None, str]:
    """
    Encrypts a request using hybrid encryption.

    :param data: The dictionary to be encrypted
    :type data: dict[str, Any] | None
    :param key: The symmetric key to encrypt the data, which can be a session key or an autogenerated one.
    :type key: bytes
    :param public_key: The public key to encrypt the symmetric key
    :type public_key: RSAPublicKey

    :return: The encrypted symmetric key, the encrypted data and the IV
    :rtype: tuple[str, str | None, str]
    """
    iv = os.urandom(16)
    key_b64 = encrypt_key(key, public_key)

    if data is None:
        return key_b64, None, b64_encode_and_escape(iv)

    data_bytes = json.dumps(data).encode()
    data_bytes = encrypt_symmetric(data_bytes, key, iv).decode()

    return key_b64, data_bytes, b64_encode_and_escape(iv)


def decrypt_symmetric(data: bytes, key: bytes, iv: bytes) -> bytes:
    data = base64.decodebytes(data)
    algorithm = algorithms.AES(key)
    mode = modes.CTR(iv)
    decryptor = Cipher(algorithm, mode).decryptor()

    return decryptor.update(data) + decryptor.finalize()


def decrypt_asymmetric(data: bytes, private_key: RSAPrivateKey) -> bytes:
    return private_key.decrypt(data, padding.PKCS1v15())


def decrypt_dict(
    key: str, data: str, iv: str, private_key: RSAPrivateKey
) -> dict[str, Any]:
    """
    Decrypts a dictionary using hybrid encryption.

    :param key: The encrypted symmetric key
    :type key: str
    :param data: The encrypted data
    :type data: str
    :param iv: The IV used to encrypt the data
    :type iv: str
    :param private_key: The private key to decrypt the symmetric key
    :type private_key: RSAPrivateKey

    :return: The decrypted dictionary
    :rtype: dict[str, Any]
    """
    key = b64_decode_and_unescape(key)
    key = decrypt_asymmetric(key, private_key)

    iv = b64_decode_and_unescape(iv)

    data = b64_decode_and_unescape(data)
    data = decrypt_symmetric(data, key, iv)

    return json.loads(data)
