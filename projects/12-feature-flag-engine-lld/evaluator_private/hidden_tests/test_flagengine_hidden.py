"""Hidden tests — Project 12 (Feature Flag Rule Engine LLD).

Copy this file into candidate/tests/ before running `pytest -q` from
candidate/. Covers:

- The key design-quality check: RuleChain must depend only on the FlagRule
  interface (calling .decide(context) and checking for None), not on the
  concrete DenyListRule / AllowListRule / PercentageRolloutRule types.
- Consistency between PercentageRolloutFlag and PercentageRolloutRule (no
  duplicated, divergently-drifting bucketing logic).
- RuleChain must not hardcode a specific rule ordering — it just walks
  whatever list it's given.
- A larger-scale, tighter-tolerance statistical uniformity check.
"""

from flagengine import (
    AllowListRule,
    DenyListRule,
    FlagRule,
    PercentageRolloutFlag,
    PercentageRolloutRule,
    RuleChain,
)


# ---------------------------------------------------------------------------
# RuleChain must be genuinely polymorphic over FlagRule
# ---------------------------------------------------------------------------
#
# Each custom rule below is a small, self-contained FlagRule implementation
# that RuleChain (and DenyListRule/AllowListRule/PercentageRolloutRule) has
# never seen. They must work as drop-in rules with ZERO changes to
# RuleChain or any of the built-in rule classes.


class AlwaysOnRule(FlagRule):
    """A trivial custom rule: always decides True, never defers."""

    def decide(self, context: dict) -> bool | None:
        return True


class AlwaysOffRule(FlagRule):
    """A trivial custom rule: always decides False, never defers."""

    def decide(self, context: dict) -> bool | None:
        return False


class BusinessHoursRule(FlagRule):
    """A custom rule with its own logic unrelated to allow/deny/rollout:
    decides True during "business hours" (9 <= hour < 17), defers (None)
    if context["hour"] is missing or outside that window."""

    def decide(self, context: dict) -> bool | None:
        hour = context.get("hour")
        if hour is None:
            return None
        if 9 <= hour < 17:
            return True
        return None


def test_chain_honors_a_custom_rule_that_is_the_only_rule():
    # A RuleChain that branches on isinstance(rule, <built-in type>) instead
    # of calling rule.decide(context) will either crash on AlwaysOffRule or
    # silently skip it (treating it as if it deferred), producing `default`
    # (True) instead of the rule's actual decision (False).
    chain = RuleChain(rules=[AlwaysOffRule()], default=True)
    assert chain.is_enabled({"user_id": "anyone"}) is False


def test_chain_custom_rule_decision_beats_default_when_placed_after_known_rules():
    chain = RuleChain(
        rules=[
            DenyListRule(user_ids=set()),
            AllowListRule(user_ids=set()),
            AlwaysOnRule(),
        ],
        default=False,
    )
    # Both built-in rules defer for this user; AlwaysOnRule must be the one
    # that actually decides -- an implementation that only recognizes the
    # two built-in rule types would fall through to `default` (False) here,
    # which is wrong.
    assert chain.is_enabled({"user_id": "anyone"}) is True


def test_chain_falls_through_a_deferring_custom_rule_to_the_next_rule():
    chain = RuleChain(
        rules=[
            BusinessHoursRule(),
            PercentageRolloutRule(flag_name="hidden-biz-hours", rollout_percentage=0.0),
        ],
        default=False,
    )
    # Outside business hours: BusinessHoursRule defers, so the 0% rollout
    # rule after it must be the one that decides (False).
    assert chain.is_enabled({"user_id": "u1", "hour": 3}) is False
    # During business hours: BusinessHoursRule itself must decide True
    # directly, without falling through to the 0% rollout rule -- an
    # implementation that doesn't recognize BusinessHoursRule (and silently
    # skips it, treating it as always deferring) would incorrectly reach
    # the rollout rule here and return False instead of True.
    assert chain.is_enabled({"user_id": "u1", "hour": 10}) is True


def test_chain_mixes_a_custom_rule_with_built_in_rules_in_the_middle():
    chain = RuleChain(
        rules=[
            DenyListRule(user_ids={"banned"}),
            BusinessHoursRule(),
            AllowListRule(user_ids=set()),
            PercentageRolloutRule(flag_name="hidden-mixed", rollout_percentage=0.0),
        ],
        default=False,
    )
    # Deny still wins first, regardless of the custom rule sitting later.
    assert chain.is_enabled({"user_id": "banned", "hour": 10}) is False
    # Not denied; business hours decides directly.
    assert chain.is_enabled({"user_id": "other", "hour": 10}) is True
    # Not denied, outside business hours (defers), allow-list empty
    # (defers), rollout is 0% (decides False).
    assert chain.is_enabled({"user_id": "other", "hour": 3}) is False


# ---------------------------------------------------------------------------
# PercentageRolloutRule must agree with PercentageRolloutFlag
# ---------------------------------------------------------------------------


def test_percentage_rollout_rule_agrees_with_percentage_rollout_flag():
    flag_name = "agree-check"
    percentage = 37.0
    flag = PercentageRolloutFlag(flag_name=flag_name, rollout_percentage=percentage)
    rule = PercentageRolloutRule(flag_name=flag_name, rollout_percentage=percentage)

    for i in range(300):
        context = {"user_id": f"user-{i}"}
        assert rule.decide(context) == flag.is_enabled(context)


def test_percentage_rollout_rule_never_defers():
    rule = PercentageRolloutRule(flag_name="never-defers", rollout_percentage=50.0)
    for i in range(100):
        assert rule.decide({"user_id": f"user-{i}"}) in (True, False)


# ---------------------------------------------------------------------------
# RuleChain must not hardcode a rule ordering -- it just walks the list
# ---------------------------------------------------------------------------


def test_rule_chain_respects_whatever_order_it_is_given():
    # Rollout first: since it's 0% for everyone, it decides before the
    # allow/deny rules ever get a turn, regardless of what they say.
    rollout_first = RuleChain(
        rules=[
            PercentageRolloutRule(flag_name="order-check", rollout_percentage=0.0),
            AllowListRule(user_ids={"vip"}),
            DenyListRule(user_ids={"vip"}),
        ],
        default=True,
    )
    assert rollout_first.is_enabled({"user_id": "vip"}) is False

    # Allow-list placed before deny-list: in THIS chain, allow must win for
    # a user in both lists, precisely because of the order given -- the
    # built-in "deny beats allow" priority from the README only holds when
    # deny is listed first.
    allow_before_deny = RuleChain(
        rules=[
            AllowListRule(user_ids={"vip"}),
            DenyListRule(user_ids={"vip"}),
        ],
        default=False,
    )
    assert allow_before_deny.is_enabled({"user_id": "vip"}) is True


# ---------------------------------------------------------------------------
# Larger-scale statistical uniformity check (tighter tolerance than the
# public test, still safe/non-flaky for a correct hash-based implementation)
# ---------------------------------------------------------------------------


def test_large_scale_rollout_uniformity_tighter_tolerance():
    flag = PercentageRolloutFlag(flag_name="large-scale-stat-check", rollout_percentage=30.0)

    n = 5000
    enabled_count = sum(
        1 for i in range(n) if flag.is_enabled({"user_id": f"synthetic-user-{i}"})
    )
    ratio = enabled_count / n

    assert 0.26 <= ratio <= 0.34
