"""Public interfaces for the feature-flag engine.

This file is fully implemented and given to you as-is — you should not need
to (and should not) modify it. Everything you build should depend only on
these interfaces, not on any concrete implementation.
"""

from abc import ABC, abstractmethod


class FeatureFlag(ABC):
    """A feature flag: something that can decide, for a given evaluation
    context, whether it is on or off.

    `context` is a plain dict describing who/what is being evaluated (e.g.
    `{"user_id": "u-123"}`). Implementations are expected to depend only on
    the keys they document needing, and should treat unrelated keys as
    ignorable.
    """

    @abstractmethod
    def is_enabled(self, context: dict) -> bool:
        """Return whether the flag is on for this context (e.g.
        context["user_id"])."""
        raise NotImplementedError


class FlagRule(ABC):
    """One rule in a chain of rules that together decide a flag's value.

    Unlike `FeatureFlag.is_enabled`, a single rule does not have to have an
    opinion about every context it's asked about — it may not apply here at
    all, in which case evaluation should move on to the next rule.
    """

    @abstractmethod
    def decide(self, context: dict) -> bool | None:
        """Return True or False if this rule has a definitive opinion for
        this context, or None if this rule doesn't apply here and
        evaluation should defer to the next rule."""
        raise NotImplementedError
