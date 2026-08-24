from typing import Optional

from app.models.schemas import ProfileUpdateRequest, UserProfile
from app.repositories.profile_repository import ProfileRepository


class ProfileService:
    """Applies partial updates to a user's stored profile settings.

    Business rule: PATCH is a *partial* update. A field the caller omits
    from the request body must be left exactly as it was; only fields the
    caller actually included in the request should change. This means we
    must distinguish "field was not provided at all" from "field was
    provided as null/None" -- ``model_dump(exclude_unset=True)`` does this
    correctly (it only includes keys the caller actually set on the
    request, including ones explicitly set to ``None``), whereas plain
    ``model_dump()`` or ``model_dump(exclude_none=True)`` do not:

      * plain ``model_dump()`` includes every field at its current value
        (``None`` for anything omitted), so omitted fields get wiped.
      * ``exclude_none=True`` drops every field currently ``None``,
        *including* fields the caller explicitly set to ``null`` to
        intentionally clear them -- so an explicit "clear this field"
        request would silently no-op instead of clearing it.
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

        update_data = request.model_dump(exclude_unset=True)
        updated = profile.model_copy(update=update_data)

        self._repository.save(updated)
        return updated
