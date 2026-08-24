"""Part 2 — implement RuleChain.

See the "Part 2 — Follow-up" section of the README for the full
requirements. This file only gives you the shape of the class; the body is
up to you.

Do not start this file until Part 1 (percentage_rollout.py) is done and
tested — the README explains why.
"""

from .base import FeatureFlag, FlagRule


class RuleChain(FeatureFlag):
    def __init__(self, rules: list[FlagRule], default: bool):
        raise NotImplementedError

    def is_enabled(self, context: dict) -> bool:
        raise NotImplementedError
