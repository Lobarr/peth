import os
import json
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.kdf import x963kdf
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from lib.helper import Helper

class Crypto:
  @staticmethod
  def generate_key_pair() -> tuple:
    """
    generates key pair
    @returns: public and private key pair
    """
    private_key = ec.generate_private_key(
      ec.SECP256K1(), default_backend()
    )
    serialized_private_key = private_key.private_bytes(
      encoding=serialization.Encoding.PEM,
      format=serialization.PrivateFormat.TraditionalOpenSSL,
      encryption_algorithm=serialization.NoEncryption()
    ).hex()
    public_key = private_key.public_key()
    serialized_public_key = public_key.public_bytes(
      encoding=serialization.Encoding.PEM,
      format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).hex()

    return (serialized_private_key, serialized_public_key)

  @staticmethod
  def sign(data: object, private_key: str) -> str:
    """
    signs a message
    @param message: (object) message to sign
    @param private_key: (str) private key to sign with
    """
    private_key_bytes = serialization.load_pem_private_key(
      bytes.fromhex(private_key),
      password=None,
      backend=default_backend()
    )
    data_bytes = Helper.object_to_bytes(data)
    signature = private_key_bytes.sign(data_bytes, ec.ECDSA(hashes.SHA256()))
    return signature.hex()

  @staticmethod
  def verify(data: object, signature: str, public_key: str) -> bool:
    """
    verfies message with digital signature
    @param message: (object) message to verify
    @param signature: (str) signature to verify message with
    @param public_key: (str) public key to verify message with
    """
    try:
      public_key_bytes = serialization.load_pem_public_key(
        public_key.encode('utf-8'),
        backend=default_backend()
      )
      signature_bytes = bytes.fromhex(signature)
      data_bytes = Helper.object_to_bytes(data)
      public_key_bytes.verify(signature_bytes, data_bytes, ec.ECDSA(hashes.SHA256()))
      return True
    except InvalidSignature:
      return False
