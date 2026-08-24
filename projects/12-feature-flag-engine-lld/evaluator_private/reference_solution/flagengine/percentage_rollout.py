"""Reference solution — PercentageRolloutFlag.

Also home to `_bucket_for`, the shared deterministic bucketing helper used by
both `PercentageRolloutFlag` and `PercentageRolloutRule` (rules.py), so the
two never drift out of sync with each other.
"""

import hashlib

from .base import FeatureFlag


def _bucket_for(flag_name: str, user_id: str) -> int:
    """Deterministically map (flag_name, user_id) to an integer bucket in
    [0, 100).

    Uses `hashlib.sha256` rather than Python's built-in `hash()` on purpose:
    `hash()` on strings is randomized per-process via `PYTHONHASHSEED`
    unless that's explicitly disabled, so the same (flag_name, user_id)
    pair could land in a different bucket after every process restart —
    which would silently violate the "same user always gets the same
    result, forever" requirement. `hashlib.sha256` is stable across
    processes, machines, and Python versions.
    """
    digest = hashlib.sha256(f"{flag_name}:{user_id}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], byteorder="big") % 100


class PercentageRolloutFlag(FeatureFlag):
    def __init__(self, flag_name: str, rollout_percentage: float):
        if not (0 <= rollout_percentage <= 100):
            raise ValueError("rollout_percentage must be between 0 and 100")

        self._flag_name = flag_name
        self._rollout_percentage = rollout_percentage

    def is_enabled(self, context: dict) -> bool:
        user_id = context["user_id"]
        return _bucket_for(self._flag_name, user_id) < self._rollout_percentage
