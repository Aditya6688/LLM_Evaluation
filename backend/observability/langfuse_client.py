import logging

from backend.config import settings

logger = logging.getLogger(__name__)

_langfuse = None


def get_langfuse():
    """Get or initialize the Langfuse client. Returns None if not configured."""
    global _langfuse
    if _langfuse is not None:
        return _langfuse

    if not settings.langfuse_enabled:
        logger.info("Langfuse not configured — observability disabled")
        return None

    try:
        from langfuse import Langfuse

        _langfuse = Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host,
        )
        logger.info("Langfuse initialized at %s", settings.langfuse_host)
        return _langfuse
    except ImportError:
        logger.warning("langfuse package not installed — observability disabled")
        return None
    except Exception:
        logger.exception("Failed to initialize Langfuse")
        return None


def flush_langfuse():
    """Flush pending Langfuse events. Call on app shutdown."""
    if _langfuse is not None:
        _langfuse.flush()
