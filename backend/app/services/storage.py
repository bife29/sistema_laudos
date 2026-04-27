"""Serviço de armazenamento — parametrizável (local | S3 | MinIO)."""

import shutil
from pathlib import Path
from abc import ABC, abstractmethod

from backend.app.core.config import get_settings


class StorageProvider(ABC):
    @abstractmethod
    async def save(self, file_bytes: bytes, destination: str) -> str:
        ...

    @abstractmethod
    async def load(self, path: str) -> bytes:
        ...

    @abstractmethod
    async def delete(self, path: str) -> None:
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


class S3Storage(StorageProvider):
    """Placeholder para S3/MinIO — implementar quando necessário."""

    def __init__(self, bucket: str, region: str, access_key: str, secret_key: str, endpoint_url: str = ""):
        self.bucket = bucket
        self.region = region
        self.access_key = access_key
        self.secret_key = secret_key
        self.endpoint_url = endpoint_url

    async def save(self, file_bytes: bytes, destination: str) -> str:
        # TODO: implementar com boto3/aioboto3
        raise NotImplementedError("S3 storage será implementado para produção")

    async def load(self, path: str) -> bytes:
        raise NotImplementedError("S3 storage será implementado para produção")

    async def delete(self, path: str) -> None:
        raise NotImplementedError("S3 storage será implementado para produção")


def get_storage() -> StorageProvider:
    """Factory: retorna o provider configurado no .env"""
    settings = get_settings()
    if settings.storage_provider == "local":
        return LocalStorage(settings.storage_local_path)
    elif settings.storage_provider in ("s3", "minio"):
        return S3Storage(
            bucket=settings.storage_s3_bucket,
            region=settings.storage_s3_region,
            access_key=settings.storage_s3_access_key,
            secret_key=settings.storage_s3_secret_key,
            endpoint_url=settings.storage_s3_endpoint_url,
        )
    else:
        raise ValueError(f"Storage provider não suportado: {settings.storage_provider}")
