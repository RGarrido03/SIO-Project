import base64


def b64_encode_and_escape(data: bytes) -> bytes:
    return base64.encodebytes(data).replace(b"\n", b"\\n").replace(b"\r", b"\\r")


def b64_decode_and_unescape(data: bytes) -> bytes:
    return base64.decodebytes(data.replace(b"\\n", b"\n").replace(b"\\r", b"\r"))
