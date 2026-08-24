"""Reference solution — RuleChain.

The whole point of this class: it must depend only on the `FlagRule`
interface (specifically, calling `.decide(context)` and checking for
`None`), never on any concrete rule type. It should work correctly with any
list of `FlagRule` objects, including rule types that don't exist yet at the
time this class is written.
"""

from .base import FeatureFlag, FlagRule


class RuleChain(FeatureFlag):
    def __init__(self, rules: list[FlagRule], default: bool):
        self._rules = list(rules)
        self._default = default

    def is_enabled(self, context: dict) -> bool:
        for rule in self._rules:
            result = rule.decide(context)
            if result is not None:
                return result
        return self._default
