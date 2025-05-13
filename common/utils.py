import hashlib

class Utils:
    def password_secure(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def password_verify(self, input_password: str, stored_hash: str) -> bool:
        return self.password_secure(input_password) == stored_hash
