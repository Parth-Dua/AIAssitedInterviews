import hashlib
import json


def compute_export_result(payload: dict) -> str:
    """Computes an export result reference string from a job payload.

    A pure function of `payload`: the same payload always produces the
    same return value. Represents the work a worker process would run
    before reporting back through the finish callback. No I/O, no
    randomness, no timestamps.
    """
    canonical = json.dumps(payload, sort_keys=True, default=str)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]
    fmt = payload.get("format", "csv") if isinstance(payload, dict) else "csv"
    return f"export-{digest}.{fmt}"
