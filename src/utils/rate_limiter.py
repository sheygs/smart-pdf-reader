import time
from typing import Tuple, Optional
from config import rate_limit_config


class RateLimiter:
    """Handles rate limiting for user queries."""

    @staticmethod
    def check_limit(session_manager) -> Tuple[bool, Optional[str]]:
        """
        Check if user has exceeded rate limits.

        Args:
            session_manager: SessionManager instance for accessing session state

        Returns:
            Tuple of (is_allowed, error_message).
            If is_allowed is True, error_message is None.
        """
        query_count = session_manager.get("query_count", 0)
        last_query_time = session_manager.get("last_query_time", 0.0)

        # cooldown check
        if time.time() - last_query_time < rate_limit_config.cooldown_seconds:
            return False, "Please wait before sending another query."

        # max queries check
        if query_count >= rate_limit_config.max_queries_per_session:
            return False, "Session query limit reached. Please refresh the page."

        return True, None

    @staticmethod
    def record_query(session_manager):
        """
        Record a query for rate limiting purposes.

        Args:
            session_manager: SessionManager instance for accessing session state
        """
        current_count = session_manager.get("query_count", 0)
        session_manager.set("query_count", current_count + 1)
        session_manager.set("last_query_time", time.time())
