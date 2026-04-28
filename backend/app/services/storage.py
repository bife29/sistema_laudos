"""Serviço de armazenamento — parametrizável (local | s3/r2/minio)."""

import io
import logging
from pathlib import Path
from abc import ABC, abstractmethod

from backend.app.core.config import get_settings

logger = logging.getLogger(__name__)


class StorageProvider(ABC):
    @abstractmethod
    async def save(self, file_bytes: bytes, destination: str) -> str:
        """Salva arquivo e retorna identificador (path local ou key S3)."""
        ...

    @abstractmethod
    async def load(self, path: str) -> bytes:
        """Carrega bytes do arquivo."""
        ...

    @abstractmethod
    async def delete(self, path: str) -> None:
        """Remove arquivo."""
        ...

    @abstractmethod
    async def exists(self, path: str) -> bool:
        """Verifica se arquivo existe."""
        ...


class LocalStorage(StorageProvider):
    def __init__(self, base_path: str):
        self.base = Path(base_path)
        self.base.mkdir(parents=True, exist_ok=True)

    async def save(self, file_bytes: bytes, destination: str) -> str:
        full_path = self.base / destination
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(file_bytes)
        return str(full_path)

    async def load(self, path: str) -> bytes:
        return Path(path).read_bytes()

    async def delete(self, path: str) -> None:
        p = Path(path)
        if p.exists():
            p.unlink()

    async def exists(self, path: str) -> bool:
        return Path(path).exists()


class S3Storage(StorageProvider):
    """Storage S3-compatível — funciona com AWS S3, Cloudflare R2 e MinIO."""

    def __init__(self, bucket: str, region: str, access_key: str, secret_key: str, endpoint_url: str = ""):
        import boto3
        self.bucket = bucket
        client_kwargs = {
            "service_name": "s3",
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "region_name": region or "auto",
        }
        if endpoint_url:
            client_kwargs["endpoint_url"] = endpoint_url
        self.client = boto3.client(**client_kwargs)
        logger.info("S3Storage inicializado: bucket=%s endpoint=%s", bucket, endpoint_url or "AWS default")

    async def save(self, file_bytes: bytes, destination: str) -> str:
        self.client.upload_fileobj(
            io.BytesIO(file_bytes),
            self.bucket,
            destination,
        )
        logger.info("S3 upload: %s (%d bytes)", destination, len(file_bytes))
        return destination  # Retorna a key S3 (não path local)

    async def load(self, path: str) -> bytes:
        buf = io.BytesIO()
        self.client.download_fileobj(self.bucket, path, buf)
        buf.seek(0)
        return buf.read()

    async def delete(self, path: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=path)
        logger.info("S3 delete: %s", path)

    async def exists(self, path: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=path)
            return True
        except self.client.exceptions.ClientError:
            return False


_storage_instance: StorageProvider | None = None


def get_storage() -> StorageProvider:
    """Factory singleton: retorna o provider configurado no .env"""
    global _storage_instance
    if _storage_instance is not None:
        return _storage_instance

    settings = get_settings()
    if settings.storage_provider == "local":
        _storage_instance = LocalStorage(settings.storage_local_path)
    elif settings.storage_provider in ("s3", "r2", "minio"):
        _storage_instance = S3Storage(
            bucket=settings.storage_s3_bucket,
            region=settings.storage_s3_region,
            access_key=settings.storage_s3_access_key,
            secret_key=settings.storage_s3_secret_key,
            endpoint_url=settings.storage_s3_endpoint_url,
        )
    else:
        raise ValueError(f"Storage provider não suportado: {settings.storage_provider}")

    return _storage_instance
