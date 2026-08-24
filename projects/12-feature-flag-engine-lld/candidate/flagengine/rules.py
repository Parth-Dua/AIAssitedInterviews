"""Part 2 — implement AllowListRule, DenyListRule, and PercentageRolloutRule.

See the "Part 2 — Follow-up" section of the README for the full
requirements. This file only gives you the shape of each class; the bodies
are up to you.

Do not start this file until Part 1 (percentage_rollout.py) is done and
tested — the README explains why.
"""

from .base import FlagRule


class DenyListRule(FlagRule):
    def __init__(self, user_ids: set[str]):
        raise NotImplementedError

    def decide(self, context: dict) -> bool | None:
        raise NotImplementedError


class AllowListRule(FlagRule):
    def __init__(self, user_ids: set[str]):
        raise NotImplementedError

    def decide(self, context: dict) -> bool | None:
        raise NotImplementedError


class PercentageRolloutRule(FlagRule):
    def __init__(self, flag_name: str, rollout_percentage: float):
        raise NotImplementedError

    def decide(self, context: dict) -> bool | None:
        raise NotImplementedError
