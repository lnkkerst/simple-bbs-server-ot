from Crypto.Hash import SHA256


def hash_password(plain_password: str, salt: str) -> str:
    h = SHA256.new(plain_password.encode())
    h.update(salt.encode())
    return h.hexdigest()
