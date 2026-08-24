"""Public interface for all rate limiting strategies.

This file is fully implemented and given to you as-is — you should not need
to (and should not) modify it. Everything you build should depend only on
this interface, not on any concrete implementation.
"""

from abc import ABC, abstractmethod


class RateLimiter(ABC):
    """A strategy for deciding whether a request identified by a string key
    should be allowed right now.

    Implementations are expected to track state per distinct `key`
    independently — calls for one key must never affect the outcome for a
    different key.
    """

    @abstractmethod
    def allow_request(self, key: str) -> bool:
        """Return True if a request identified by `key` should be allowed
        right now (and record/consume whatever capacity that implies),
        False if it should be rejected (consuming nothing).

        Calls for different keys must be tracked independently.
        """
        raise NotImplementedError
