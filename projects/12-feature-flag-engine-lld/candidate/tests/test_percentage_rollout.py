"""Part 1 public tests for PercentageRolloutFlag."""

from flagengine import PercentageRolloutFlag


def test_same_user_gets_same_result_across_many_repeated_calls():
    flag = PercentageRolloutFlag(flag_name="checkout-v2", rollout_percentage=50.0)

    first_result = flag.is_enabled({"user_id": "user-42"})
    for _ in range(50):
        assert flag.is_enabled({"user_id": "user-42"}) == first_result


def test_zero_percent_rollout_disables_everyone():
    flag = PercentageRolloutFlag(flag_name="checkout-v2", rollout_percentage=0.0)

    for i in range(200):
        assert flag.is_enabled({"user_id": f"user-{i}"}) is False


def test_hundred_percent_rollout_enables_everyone():
    flag = PercentageRolloutFlag(flag_name="checkout-v2", rollout_percentage=100.0)

    for i in range(200):
        assert flag.is_enabled({"user_id": f"user-{i}"}) is True


def test_moderate_rollout_is_approximately_uniform_across_many_users():
    flag = PercentageRolloutFlag(flag_name="checkout-v2", rollout_percentage=50.0)

    user_ids = [f"user-{i}" for i in range(250)]
    enabled_count = sum(1 for uid in user_ids if flag.is_enabled({"user_id": uid}))

    # This is a statistical property, not exact — the tolerance below is
    # intentionally wide so this never flakes for a correctly-implemented,
    # roughly-uniform hash-based bucketing scheme.
    assert 0.35 * len(user_ids) <= enabled_count <= 0.65 * len(user_ids)


def test_different_flag_names_can_diverge_for_the_same_user():
    # Bucketing must be per-flag, not purely per-user — otherwise every flag
    # in the system would turn on for exactly the same subset of users.
    flag_a = PercentageRolloutFlag(flag_name="flag-a", rollout_percentage=50.0)
    flag_b = PercentageRolloutFlag(flag_name="flag-b", rollout_percentage=50.0)

    results_a = [flag_a.is_enabled({"user_id": f"user-{i}"}) for i in range(200)]
    results_b = [flag_b.is_enabled({"user_id": f"user-{i}"}) for i in range(200)]

    # Not every user should land the same way on both flags. (If bucketing
    # ignored flag_name entirely, results_a and results_b would be
    # identical for every single user.)
    assert results_a != results_b
