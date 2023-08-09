import collections
import time
from enum import Enum
from .config import get_settings, Limit


conf = get_settings()


class RateLimit(Limit, Enum):
    PDF_FULL = conf.hb_pdf_full_limit.limit, conf.hb_pdf_full_limit.minutes
    PDF_PAGE = conf.hb_pdf_page_limit.limit, conf.hb_pdf_page_limit.minutes
    IMAGE_PAGE = conf.hb_image_page_limit.limit, conf.hb_image_page_limit.minutes


class RateLimiter:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not RateLimiter._instance:
            RateLimiter._instance = super().__new__(cls)
        return RateLimiter._instance

    def __init__(self):
        self.user_rates: dict[tuple[str | int, str], tuple[float, int]] = collections.defaultdict(lambda: (0, 0))

    def get_seconds_to_wait(self, user_id: str | int, rate_limit_type: RateLimit) -> int:
        """Get the number of seconds to wait before making a request."""
        now = time.time()
        last_time, count = self.user_rates[user_id, rate_limit_type.name]
        if now - last_time > rate_limit_type.seconds:
            self.user_rates[user_id, rate_limit_type.name] = (now, 1)
            return 0
        if count >= rate_limit_type.limit:
            return int(rate_limit_type.seconds - (now - last_time))
        self.user_rates[user_id, rate_limit_type.name] = (last_time, count + 1)
        return 0


limiter = RateLimiter()  # Singleton
