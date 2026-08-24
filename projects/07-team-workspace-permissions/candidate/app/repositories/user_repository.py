from app.models.schemas import User


class UserRepository:
    """In-memory store of users.

    Users carry no permission information themselves — see
    MembershipRepository for per-workspace roles.
    """

    def __init__(self):
        self._users: dict[int, User] = {
            1: User(id=1, name="Alice Chen"),
            2: User(id=2, name="Bob Nguyen"),
            3: User(id=3, name="Carol Diaz"),
        }

    def get_user(self, user_id: int) -> User | None:
        return self._users.get(user_id)

    def list_users(self) -> list[User]:
        return list(self._users.values())
