import os

host: str = os.getenv("REZKA_HOSTNAME", "https://rezka.ag")
concurrency_limit: int = int(os.getenv("REZKA_CONCURRENCY_LIMIT", 60))
max_retry: int = int(os.getenv("REZKA_MAX_RETRY", 5))
retry_delay: int = int(os.getenv("REZKA_RETRY_DELAY", 2))
