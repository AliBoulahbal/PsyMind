from io import BytesIO
from minio import Minio
from app.core.config import settings

def client():
    return Minio(settings.minio_endpoint,
                 access_key=settings.minio_access_key,
                 secret_key=settings.minio_secret_key,
                 secure=False)

def ensure_bucket():
    c=client()
    if not c.bucket_exists(settings.minio_bucket): c.make_bucket(settings.minio_bucket)
    return c

def put_bytes(key:str,data:bytes,mime:str):
    c=ensure_bucket()
    c.put_object(settings.minio_bucket,key,BytesIO(data),len(data),content_type=mime)
