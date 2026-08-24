"""Public interfaces for the feature-flag engine (given to candidates
unmodified — mirrored here for a complete, importable reference package)."""

from abc import ABC, abstractmethod


class FeatureFlag(ABC):
    @abstractmethod
    def is_enabled(self, context: dict) -> bool:
        """Return whether the flag is on for this context (e.g.
        context["user_id"])."""
        raise NotImplementedError


class FlagRule(ABC):
    @abstractmethod
    def decide(self, context: dict) -> bool | None:
        """Return True or False if this rule has a definitive opinion for
        this context, or None if this rule doesn't apply here and
        evaluation should defer to the next rule."""
        raise NotImplementedError
