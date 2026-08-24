"""Hidden tests. Copy this file into candidate/tests/ (it is not present in
the candidate repo) and run `pytest` from candidate/ after applying a
candidate's fix, or after applying reference_solution/profile_service.py to
validate the answer key.
"""

from app.models.schemas import ProfileUpdateRequest
from app.repositories.profile_repository import ProfileRepository
from app.services.profile_service import ProfileService


def make_service() -> ProfileService:
    return ProfileService(ProfileRepository())


def test_patch_only_email_notifications_preserves_other_fields():
    service = make_service()
    request = ProfileUpdateRequest(email_notifications=False)
    updated = service.update_profile(1, request)

    assert updated is not None
    assert updated.email_notifications is False
    assert updated.display_name == "Alice Chen"
    assert updated.bio == "Loves hiking and photography"
    assert updated.timezone == "America/Chicago"


def test_patch_explicit_null_clears_nullable_field():
    """A caller sending an *explicit* `null` for a nullable field (bio) is
    intentionally clearing it -- this must actually take effect. This is
    the case that a naive `exclude_none=True` "fix" gets wrong: it drops
    explicit nulls along with omitted fields, so the field never clears.
    """
    service = make_service()
    request = ProfileUpdateRequest.model_validate({"bio": None})
    assert "bio" in request.model_fields_set

    updated = service.update_profile(1, request)

    assert updated is not None
    assert updated.bio is None, (
        "an explicit `null` for bio must clear it, not be ignored"
    )
    # Untouched fields must still be preserved.
    assert updated.display_name == "Alice Chen"
    assert updated.timezone == "America/Chicago"
    assert updated.email_notifications is True


def test_patch_empty_body_changes_nothing():
    service = make_service()
    request = ProfileUpdateRequest()
    updated = service.update_profile(1, request)

    assert updated is not None
    assert updated.display_name == "Alice Chen"
    assert updated.bio == "Loves hiking and photography"
    assert updated.timezone == "America/Chicago"
    assert updated.email_notifications is True


def test_sequential_patches_accumulate_correctly():
    """Several one-field PATCHes in a row should accumulate, not clobber
    each other's changes.
    """
    service = make_service()

    service.update_profile(2, ProfileUpdateRequest(timezone="Asia/Tokyo"))
    service.update_profile(2, ProfileUpdateRequest(email_notifications=True))
    final = service.update_profile(
        2, ProfileUpdateRequest(display_name="Bob M.")
    )

    assert final is not None
    assert final.display_name == "Bob M."
    assert final.timezone == "Asia/Tokyo"
    assert final.email_notifications is True
    assert final.bio == "Full-stack engineer, coffee enthusiast"


def test_patch_response_reflects_merged_full_profile():
    service = make_service()
    request = ProfileUpdateRequest(bio="Trail running now")
    updated = service.update_profile(1, request)

    assert updated is not None
    assert updated.user_id == 1
    assert updated.display_name == "Alice Chen"
    assert updated.bio == "Trail running now"
    assert updated.timezone == "America/Chicago"
    assert updated.email_notifications is True
