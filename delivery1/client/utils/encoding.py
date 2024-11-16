import base64


def b64_encode_and_escape(data: bytes) -> str:
    return base64.encodebytes(data).decode().replace("\n", "\\n").replace("\r", "\\r")


def b64_decode_and_unescape(data: str) -> bytes:
    return base64.decodebytes(
        data.encode().replace(b"\\n", b"\n").replace(b"\\r", b"\r")
    )
