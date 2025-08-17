from functools import cache

from docserverlib import DocserverClient

from .config import settings


@cache
def get_docserver_client() -> DocserverClient:
    if not settings.DOCSERVER:
        raise ValueError("DOCSERVER configuration not configured")

    return DocserverClient(
        **settings.DOCSERVER.model_dump(by_alias=True),
    )
