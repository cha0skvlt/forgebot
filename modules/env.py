import os


def get_env(name: str, default: str | None = None, *, required: bool = False) -> str | None:
    value = os.getenv(name)
    if value:
        return value
    if default is not None:
        return default
    if required:
        raise RuntimeError(f"{name} not set")
    return None


OWNER_ID = int(get_env("OWNER_ID", required=True))

