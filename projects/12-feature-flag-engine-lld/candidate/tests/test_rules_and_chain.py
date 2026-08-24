"""Part 2 public tests for AllowListRule, DenyListRule, PercentageRolloutRule,
and RuleChain.

Only start on these once Part 1 (test_percentage_rollout.py) is fully
passing — see the README.
"""

from flagengine import AllowListRule, DenyListRule, PercentageRolloutRule, RuleChain


def test_denylisted_user_is_off_even_with_full_rollout():
    chain = RuleChain(
        rules=[
            DenyListRule(user_ids={"investigated-1"}),
            AllowListRule(user_ids=set()),
            PercentageRolloutRule(flag_name="checkout-v2", rollout_percentage=100.0),
        ],
        default=False,
    )

    assert chain.is_enabled({"user_id": "investigated-1"}) is False


def test_allowlisted_user_is_on_even_with_zero_rollout():
    chain = RuleChain(
        rules=[
            DenyListRule(user_ids=set()),
            AllowListRule(user_ids={"qa-1"}),
            PercentageRolloutRule(flag_name="checkout-v2", rollout_percentage=0.0),
        ],
        default=False,
    )

    assert chain.is_enabled({"user_id": "qa-1"}) is True


def test_deny_beats_allow_when_user_is_in_both_lists():
    chain = RuleChain(
        rules=[
            DenyListRule(user_ids={"contradictory-user"}),
            AllowListRule(user_ids={"contradictory-user"}),
            PercentageRolloutRule(flag_name="checkout-v2", rollout_percentage=100.0),
        ],
        default=False,
    )

    assert chain.is_enabled({"user_id": "contradictory-user"}) is False


def test_user_in_neither_list_falls_through_to_percentage_rollout():
    chain_all_off = RuleChain(
        rules=[
            DenyListRule(user_ids=set()),
            AllowListRule(user_ids=set()),
            PercentageRolloutRule(flag_name="checkout-v2", rollout_percentage=0.0),
        ],
        default=True,  # deliberately the "wrong" answer, to prove the rule wins
    )
    assert chain_all_off.is_enabled({"user_id": "ordinary-user"}) is False

    chain_all_on = RuleChain(
        rules=[
            DenyListRule(user_ids=set()),
            AllowListRule(user_ids=set()),
            PercentageRolloutRule(flag_name="checkout-v2", rollout_percentage=100.0),
        ],
        default=False,  # deliberately the "wrong" answer, to prove the rule wins
    )
    assert chain_all_on.is_enabled({"user_id": "ordinary-user"}) is True


def test_default_is_used_only_when_the_chain_has_no_rules():
    chain_true = RuleChain(rules=[], default=True)
    chain_false = RuleChain(rules=[], default=False)

    assert chain_true.is_enabled({"user_id": "anyone"}) is True
    assert chain_false.is_enabled({"user_id": "anyone"}) is False
