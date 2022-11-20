"""
Encryption utils
"""

import json
import base64

from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
from Crypto.Cipher import AES


class Encryption:
    """
    AES-CBC encryption helper class
    """

    def __init__(self, password: str = ""):
        self.password = password.encode("ascii")

    def base64_encode(self, text: str):
        """
        Base64 encode a string
        """
        return base64.b64encode(text).decode("UTF-8")

    def base64_decode(self, text: str):
        """
        Base64 decode a string
        """
        return base64.decodebytes(text.encode("ascii"))

    def encrypt(self, data: any):
        """
        Encrypt a string
        """
        if not isinstance(data, str):
            data: str = json.dumps(data)
        data_bytes = data.encode("ascii")

        salt = get_random_bytes(32)

        encryption_key = PBKDF2(
            self.password, salt, 32, count=15000, hmac_hash_module=SHA256
        )

        cipher = AES.new(encryption_key, AES.MODE_CBC)

        cipher_text = cipher.encrypt(pad(data_bytes, AES.block_size))

        return (
            self.base64_encode(salt)
            + ":"
            + self.base64_encode(cipher.iv)
            + ":"
            + self.base64_encode(cipher_text)
        )

    def decrypt(self, encrypted_data: str, decode_json: bool = True):
        """
        Decrypt a string
        """
        data = encrypted_data.split(":")

        salt = self.base64_decode(data[0])
        cipher_iv = self.base64_decode(data[1])
        cipher_text = self.base64_decode(data[2])

        decryption_key = PBKDF2(
            self.password, salt, 32, count=15000, hmac_hash_module=SHA256
        )

        cipher = AES.new(decryption_key, AES.MODE_CBC, cipher_iv)

        decrypted = unpad(cipher.decrypt(cipher_text), AES.block_size).decode("UTF-8")

        return json.loads(decrypted) if decode_json else decrypted
