import argon2

def hash_password(password: str) -> str:
    hasher = argon2.PasswordHasher()
    return hasher.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    hasher = argon2.PasswordHasher()
    try:
        hasher.verify(hashed_password, plain_password)
        return True
    except argon2.exceptions.VerifyMismatchError:
        return False


