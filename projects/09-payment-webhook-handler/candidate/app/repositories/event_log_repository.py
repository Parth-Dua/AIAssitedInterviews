from app.models.schemas import PaymentEventIn


class EventLogRepository:
    """Audit trail of every payment webhook delivery attempt this service
    has received, including retries/duplicates of an `event_id` already
    seen before. Nothing in this class ever drops or skips an attempt —
    completeness of the audit trail is this repository's whole job.
    """

    def __init__(self):
        self._seen_event_ids: set[str] = set()
        self._log: list[PaymentEventIn] = []

    def has_seen(self, event_id: str) -> bool:
        """Whether this exact event_id has been recorded before."""
        return event_id in self._seen_event_ids

    def record(self, event: PaymentEventIn) -> None:
        """Append this delivery attempt to the log. Always runs, even for a
        duplicate delivery of an event_id already seen — the audit trail
        must reflect every attempt the processor made, not just the ones
        that changed anything.
        """
        self._seen_event_ids.add(event.event_id)
        self._log.append(event)

    def entries_for_event(self, event_id: str) -> list[PaymentEventIn]:
        """Every recorded delivery attempt for one event_id, in the order
        they arrived. Useful for confirming the audit trail captured a
        retry even when its effects weren't reapplied.
        """
        return [entry for entry in self._log if entry.event_id == event_id]

    def all_entries(self) -> list[PaymentEventIn]:
        return list(self._log)
