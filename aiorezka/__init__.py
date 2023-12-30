import logging
import os

# Network settings
host: str = os.getenv("REZKA_HOSTNAME", "https://rezka.ag")
concurrency_limit: int = int(os.getenv("REZKA_CONCURRENCY_LIMIT", 60))
max_retry: int = int(os.getenv("REZKA_MAX_RETRY", 5))
retry_delay: int = int(os.getenv("REZKA_RETRY_DELAY", 2))

# Cache settings
use_cache: bool = bool(os.getenv("REZKA_USE_CACHE", True))
cache_directory: str = os.getenv("REZKA_CACHE_DIRECTORY", "/tmp/aiorezka_cache")
memcache_max_len: int = int(os.getenv("REZKA_MEMCACHE_MAX_LEN", 1000))  # Max items in memory cache is 1000 by default
cache_ttl: int = int(os.getenv("REZKA_CACHE_TTL", 60 * 60 * 24 * 1))  # 1 day by default
max_open_files: int = int(os.getenv("REZKA_MAX_OPEN_FILES", 5000))

# Logging settings
log_level: str = os.getenv("REZKA_LOG_LEVEL", "INFO")
default_logger_name: str = os.getenv("REZKA_DEFAULT_LOGGER_NAME", "aiorezka")
