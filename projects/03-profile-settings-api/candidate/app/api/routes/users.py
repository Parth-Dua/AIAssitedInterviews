from fastapi import APIRouter, HTTPException

from app.models.schemas import ProfileUpdateRequest, UserProfile
from app.repositories.profile_repository import ProfileRepository
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/users", tags=["users"])

_repository = ProfileRepository()
_service = ProfileService(_repository)


@router.get("/{user_id}", response_model=UserProfile)
def get_user(user_id: int) -> UserProfile:
    """Return a user's current profile settings."""
    profile = _service.get_profile(user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="User not found")
    return profile


@router.patch("/{user_id}", response_model=UserProfile)
def patch_user(user_id: int, request: ProfileUpdateRequest) -> UserProfile:
    """Apply a partial update to a user's profile settings.

    Only fields present in the request body should change; any field the
    caller omits must be left untouched.
    """
    updated = _service.update_profile(user_id, request)
    if updated is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated
