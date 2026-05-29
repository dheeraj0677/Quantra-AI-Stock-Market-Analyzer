"""
Quantra — Model loader (MinIO / local filesystem).
"""

from __future__ import annotations

import logging
import os
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

_cache: dict[str, str] = {}  # model_key → local_path


def load_from_minio(
    bucket: str,
    object_name: str,
    local_dir: str | None = None,
) -> str | None:
    """
    Download a model file from MinIO and return local path.

    Caches locally to avoid re-downloads.
    """
    cache_key = f"{bucket}/{object_name}"
    if cache_key in _cache and os.path.exists(_cache[cache_key]):
        return _cache[cache_key]

    try:
        from minio import Minio

        from app.config import get_settings

        settings = get_settings()
        client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )

        if local_dir is None:
            local_dir = tempfile.mkdtemp(prefix="quantra_models_")

        local_path = os.path.join(local_dir, object_name.replace("/", "_"))
        client.fget_object(bucket, object_name, local_path)

        _cache[cache_key] = local_path
        logger.info("Downloaded model: %s → %s", cache_key, local_path)
        return local_path

    except Exception as e:
        logger.warning("MinIO download failed for %s: %s", cache_key, e)
        return None


def load_model_file(model_name: str, local_fallback: str | None = None) -> str | None:
    """
    Load a model file — tries MinIO first, then local filesystem.

    Args:
        model_name: e.g. "scorer_v1.json", "direction_v1.json"
        local_fallback: Optional local path to check first
    """
    # Check local fallback first
    if local_fallback and os.path.exists(local_fallback):
        logger.info("Using local model: %s", local_fallback)
        return local_fallback

    # Try MinIO
    from app.config import get_settings
    settings = get_settings()

    path = load_from_minio(settings.MINIO_BUCKET_MODELS, model_name)
    if path:
        return path

    # Check default local paths
    default_paths = [
        Path("models") / model_name,
        Path("app/ml/trained") / model_name,
    ]
    for p in default_paths:
        if p.exists():
            logger.info("Using default local model: %s", p)
            return str(p)

    logger.warning("Model not found: %s — using rule-based fallback", model_name)
    return None


def upload_to_minio(local_path: str, bucket: str, object_name: str) -> bool:
    """Upload a trained model to MinIO."""
    try:
        from minio import Minio

        from app.config import get_settings

        settings = get_settings()
        client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )

        # Ensure bucket exists
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)

        client.fput_object(bucket, object_name, local_path)
        logger.info("Uploaded model: %s → %s/%s", local_path, bucket, object_name)
        return True

    except Exception as e:
        logger.error("MinIO upload failed: %s", e)
        return False
