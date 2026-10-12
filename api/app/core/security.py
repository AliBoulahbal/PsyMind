from datetime import datetime,timedelta,timezone
from uuid import UUID,uuid4
import jwt
from argon2 import PasswordHasher
from app.core.config import settings
ph=PasswordHasher()
def hash_password(value:str)->str:return ph.hash(value)
def verify_password(value:str,hashed:str)->bool:
    try:return ph.verify(hashed,value)
    except Exception:return False
def create_token(*,user_id:UUID,tenant_id:UUID,role:str,permissions:list[str],token_type="access"):
    now=datetime.now(timezone.utc);ttl=timedelta(minutes=settings.access_token_minutes) if token_type=="access" else timedelta(days=settings.refresh_token_days)
    payload={"sub":str(user_id),"tenant_id":str(tenant_id),"role":role,"permissions":permissions,"type":token_type,
             "jti":str(uuid4()),"iat":int(now.timestamp()),"exp":int((now+ttl).timestamp())}
    return jwt.encode(payload,settings.secret_key,algorithm="HS256")
def decode_token(token:str)->dict:return jwt.decode(token,settings.secret_key,algorithms=["HS256"])
