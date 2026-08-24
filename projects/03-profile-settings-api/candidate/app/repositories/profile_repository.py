from typing import Optional

from app.models.schemas import UserProfile


class ProfileRepository:
    """In-memory store of user profile settings.

    Maps user_id -> UserProfile. In production this would be backed by a
    database table; for this exercise a plain dict is enough.
    """

    def __init__(self):
        self._profiles: dict[int, UserProfile] = {
            1: UserProfile(
                user_id=1,
                display_name="Alice Chen",
                bio="Loves hiking and photography",
                timezone="America/Chicago",
                email_notifications=True,
            ),
            2: UserProfile(
                user_id=2,
                display_name="Bob Martinez",
                bio="Full-stack engineer, coffee enthusiast",
                timezone="Europe/London",
                email_notifications=False,
            ),
        }

    def get(self, user_id: int) -> Optional[UserProfile]:
        return self._profiles.get(user_id)

    def save(self, profile: UserProfile) -> UserProfile:
        self._profiles[profile.user_id] = profile
        return profile
