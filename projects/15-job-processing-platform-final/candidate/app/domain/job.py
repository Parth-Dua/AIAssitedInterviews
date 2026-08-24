from dataclasses import dataclass, field


@dataclass
class Job:
    """A single export job and its current lifecycle state."""

    id: str
    payload: dict = field(default_factory=dict)
    status: str = "queued"
    result: str | None = None
    error: str | None = None
    attempt_count: int = 0
