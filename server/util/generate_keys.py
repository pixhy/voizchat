from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

if __name__ != "__main__":
    raise Exception("Utility script, only run directly")

private_key = ed25519.Ed25519PrivateKey.generate()
public_key = private_key.public_key()

private_key_bytes = private_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption())

public_key_bytes = private_key.public_key().public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)

with open("private_key.pem", "wb") as private_file:
    private_file.write(private_key_bytes)

print("Private key saved to 'private_key.pem'")

with open("public_key.pem", "wb") as public_file:
    public_file.write(public_key_bytes)

print("Public key saved to 'public_key.pem'")
