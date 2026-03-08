import logging

from app.config import settings
from app.middleware.request_id_middleware import RequestIDFilter


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO if settings.is_production else logging.DEBUG,
        format="%(asctime)s [%(request_id)s] %(name)s %(levelname)s - %(message)s",
    )
    request_id_filter = RequestIDFilter()
    for handler in logging.getLogger().handlers:
        handler.addFilter(request_id_filter)
