from app.models.schemas import ProfileUpdateRequest
from app.repositories.profile_repository import ProfileRepository
from app.services.profile_service import ProfileService


def make_service() -> ProfileService:
    return ProfileService(ProfileRepository())


def test_get_existing_profile_returns_seeded_values():
    service = make_service()
    profile = service.get_profile(1)
    assert profile is not None
    assert profile.display_name == "Alice Chen"
    assert profile.bio == "Loves hiking and photography"
    assert profile.timezone == "America/Chicago"
    assert profile.email_notifications is True


def test_patch_full_body_updates_all_fields():
    service = make_service()
    request = ProfileUpdateRequest(
        display_name="Alice C.",
        bio="Now really into rock climbing",
        timezone="America/Denver",
        email_notifications=False,
    )
    updated = service.update_profile(1, request)

    assert updated is not None
    assert updated.display_name == "Alice C."
    assert updated.bio == "Now really into rock climbing"
    assert updated.timezone == "America/Denver"
    assert updated.email_notifications is False


def test_patch_only_timezone_preserves_other_fields():
    """Bug report from support: 'Someone noticed that updating just their
    timezone also silently cleared their bio and reset their email
    notification preference -- even though they only sent `timezone` in
    the request.' A PATCH must only change the fields explicitly included
    in the request body; every other field must be left untouched.
    """
    service = make_service()
    request = ProfileUpdateRequest(timezone="America/New_York")
    updated = service.update_profile(1, request)

    assert updated is not None
    assert updated.timezone == "America/New_York"
    assert updated.display_name == "Alice Chen", (
        "display_name was not included in the request and must be unchanged"
    )
    assert updated.bio == "Loves hiking and photography", (
        "bio was not included in the request and must be unchanged"
    )
    assert updated.email_notifications is True, (
        "email_notifications was not included in the request and must be "
        "unchanged"
    )
