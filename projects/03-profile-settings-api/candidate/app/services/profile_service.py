from typing import Optional

from app.models.schemas import ProfileUpdateRequest, UserProfile
from app.repositories.profile_repository import ProfileRepository


class ProfileService:
    """Applies partial updates to a user's stored profile settings.

    Business rule: PATCH is a *partial* update. A field the caller omits
    from the request body must be left exactly as it was; only fields the
    caller actually included in the request should change.
    """

    def __init__(self, repository: ProfileRepository):
        self._repository = repository

    def get_profile(self, user_id: int) -> Optional[UserProfile]:
        return self._repository.get(user_id)

    def update_profile(
        self, user_id: int, request: ProfileUpdateRequest
    ) -> Optional[UserProfile]:
        profile = self._repository.get(user_id)
        if profile is None:
            return None

        update_data = request.model_dump()
        updated = profile.model_copy(update=update_data)

        self._repository.save(updated)
        return updated
