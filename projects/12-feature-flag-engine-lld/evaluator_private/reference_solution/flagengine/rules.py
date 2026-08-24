"""Reference solution — DenyListRule, AllowListRule, PercentageRolloutRule."""

from .base import FlagRule
from .percentage_rollout import PercentageRolloutFlag


class DenyListRule(FlagRule):
    """Never returns True — either denies (False) or defers (None)."""

    def __init__(self, user_ids: set[str]):
        self._user_ids = set(user_ids)

    def decide(self, context: dict) -> bool | None:
        if context.get("user_id") in self._user_ids:
            return False
        return None


class AllowListRule(FlagRule):
    """Never returns False — either allows (True) or defers (None)."""

    def __init__(self, user_ids: set[str]):
        self._user_ids = set(user_ids)

    def decide(self, context: dict) -> bool | None:
        if context.get("user_id") in self._user_ids:
            return True
        return None


class PercentageRolloutRule(FlagRule):
    """Always decides — never returns None.

    Composes a PercentageRolloutFlag internally instead of re-deriving the
    bucketing math, so PercentageRolloutFlag and PercentageRolloutRule can
    never disagree with each other about the same (flag_name, user_id,
    rollout_percentage).
    """

    def __init__(self, flag_name: str, rollout_percentage: float):
        self._flag = PercentageRolloutFlag(flag_name, rollout_percentage)

    def decide(self, context: dict) -> bool | None:
        return self._flag.is_enabled(context)
