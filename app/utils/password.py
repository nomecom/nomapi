import argon2

def hash_password(password: str) -> str:
    hasher = argon2.PasswordHasher()
    return hasher.hash(password)
<<<<<<< HEAD
 
=======

>>>>>>> d648c0b18eb824f3cb2cba8fc442826d52d67273
def verify_password(plain_password: str, hashed_password: str) -> bool:
    hasher = argon2.PasswordHasher()
    try:
        hasher.verify(hashed_password, plain_password)
        return True
    except argon2.exceptions.VerifyMismatchError:
<<<<<<< HEAD
        return False
=======
        return False


>>>>>>> d648c0b18eb824f3cb2cba8fc442826d52d67273
