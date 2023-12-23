import os
import sys
import threading
import time
from typing import Any, Optional

clear = "cls" if sys.platform == "win32" else "clear"


class StatsThread(threading.Thread):
    total_responses: int = 0
    error_responses: int = 0
    _thread_instance: Optional["StatsThread"] = None

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.stop_flag = threading.Event()
        if (
            StatsThread._thread_instance is not None
            and StatsThread._thread_instance.is_alive()
            and StatsThread._thread_instance != self
        ):
            raise Exception(
                "Only one instance of StatsThread is allowed.\n" "StatsThread cannot be used in multiple threads.",
            )
        StatsThread._thread_instance = self

    @classmethod
    def reset_counters(cls) -> None:
        cls.total_responses = 0
        cls.error_responses = 0

    @property
    def success_responses(self) -> int:
        return self.total_responses - self.error_responses

    def print_stats(self, start_time: float, detailed: bool = False) -> None:
        response_time = time.time() - start_time
        rps = self.success_responses / response_time if response_time else 0
        os.system(clear)
        sys.stdout.write(f"[{self.name}][{self.success_responses} requests in {response_time:.2f}s] {rps:.2f} rps\n")
        if detailed:
            sys.stdout.write(f"[{self.error_responses} errors]\n")

    def run(self) -> None:
        start_time = time.time()
        while not self.stop_flag.is_set():
            self.print_stats(start_time)
            time.sleep(0.5)
        self.print_stats(start_time, detailed=True)
        self.reset_counters()

    def stop(self) -> None:
        self.stop_flag.set()


def measure_rps(func: callable) -> callable:
    async def wrapper(*args, **kwargs) -> Any:  # noqa: ANN401
        cli = StatsThread(name=func.__name__)
        cli.start()
        try:
            result = await func(*args, **kwargs)
        except Exception as e:
            cli.stop()
            raise e
        cli.stop()
        return result

    return wrapper
