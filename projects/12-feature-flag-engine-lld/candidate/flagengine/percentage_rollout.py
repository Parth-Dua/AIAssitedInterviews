"""Part 1 — implement PercentageRolloutFlag.

See the "Part 1 — Percentage Rollout" section of the README for the full
requirements. This file only gives you the shape of the class; the body is
up to you.
"""

from .base import FeatureFlag


class PercentageRolloutFlag(FeatureFlag):
    def __init__(self, flag_name: str, rollout_percentage: float):
        raise NotImplementedError

    def is_enabled(self, context: dict) -> bool:
        raise NotImplementedError
