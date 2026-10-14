from datetime import datetime, timedelta, timezone
import hashlib, hmac, secrets
from jose import jwt, JWTError
from .config import settings
ALGORITHM="HS256"
def hash_password(password:str)->str:
    salt=secrets.token_bytes(16); digest=hashlib.pbkdf2_hmac("sha256",password.encode(),salt,310000)
    return f"pbkdf2_sha256$310000${salt.hex()}${digest.hex()}"
def verify_password(password:str, encoded:str)->bool:
    try:
        scheme,iterations,salt_hex,digest_hex=encoded.split("$")
        if scheme!="pbkdf2_sha256": return False
        digest=hashlib.pbkdf2_hmac("sha256",password.encode(),bytes.fromhex(salt_hex),int(iterations))
        return hmac.compare_digest(digest.hex(),digest_hex)
    except (ValueError,TypeError): return False
def create_token(user_id:int, role:str)->str:
    if not settings.secret_key: raise RuntimeError("Set SECRET_KEY in .env before using authentication")
    now=datetime.now(timezone.utc)
    return jwt.encode({"sub":str(user_id),"role":role,"iat":now,"exp":now+timedelta(minutes=settings.token_minutes)},settings.secret_key,algorithm=ALGORITHM)
def decode_token(token:str):
    try:return jwt.decode(token,settings.secret_key,algorithms=[ALGORITHM])
    except JWTError:return None
