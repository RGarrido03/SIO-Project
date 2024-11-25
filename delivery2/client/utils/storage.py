from pathlib import Path


def get_root_dir() -> Path:
    return Path(__file__).parent.parent


def get_storage_dir() -> Path:
    return get_root_dir() / "storage"
