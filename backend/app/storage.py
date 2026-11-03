import os
import re
from pathlib import Path
from dataclasses import dataclass
from .config import settings


class StorageConfigurationError(RuntimeError):
    pass


@dataclass(frozen=True)
class StoredObject:
    key: str
    backend: str


def safe_original_name(name: str | None) -> str:
    value = Path(name or "document").name
    value = re.sub(r"[^A-Za-z0-9._ -]", "_", value).strip(" .")
    return value[:255] or "document"


class DocumentStorage:
    def __init__(self):
        values = (settings.r2_account_id, settings.r2_access_key_id, settings.r2_secret_access_key,
                  settings.r2_bucket_name, settings.r2_endpoint_url)
        self.use_r2 = all(values)
        self.use_database = settings.app_env.lower() in {"production", "prod"} and not self.use_r2
        self.root = Path(settings.upload_dir)
        if not self.root.is_absolute():
            self.root = Path(__file__).resolve().parents[1] / self.root
        if not self.use_r2 and not self.use_database:
            self.root.mkdir(parents=True, exist_ok=True)

    def _client(self):
        import boto3
        return boto3.client("s3", endpoint_url=settings.r2_endpoint_url,
                            aws_access_key_id=settings.r2_access_key_id,
                            aws_secret_access_key=settings.r2_secret_access_key,
                            region_name="auto")

    def put(self, data: bytes, key: str, content_type: str) -> StoredObject:
        if self.use_r2:
            self._client().put_object(Bucket=settings.r2_bucket_name, Key=key, Body=data, ContentType=content_type)
        elif self.use_database:
            return StoredObject(key=key, backend="database")
        else:
            target = self.root / key
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        return StoredObject(key=key, backend="r2" if self.use_r2 else "local")

    def get(self, stored: StoredObject, database_data: bytes | None = None) -> bytes:
        if stored.backend == "r2":
            return self._client().get_object(Bucket=settings.r2_bucket_name, Key=stored.key)["Body"].read()
        if stored.backend == "database":
            if database_data is None:
                raise FileNotFoundError(stored.key)
            return database_data
        return (self.root / stored.key).read_bytes()

    def delete(self, stored: StoredObject):
        if stored.backend == "r2":
            self._client().delete_object(Bucket=settings.r2_bucket_name, Key=stored.key)
        elif stored.backend == "database":
            return
        else:
            target = self.root / stored.key
            if target.is_file():
                target.unlink()
