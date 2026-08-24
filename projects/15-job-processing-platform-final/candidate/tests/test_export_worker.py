from app.workers.export_worker import compute_export_result


def test_compute_export_result_is_deterministic_for_same_payload():
    payload = {"rows": [1, 2, 3], "format": "csv"}
    assert compute_export_result(payload) == compute_export_result(payload)


def test_compute_export_result_differs_for_different_payloads():
    a = compute_export_result({"rows": [1], "format": "csv"})
    b = compute_export_result({"rows": [2], "format": "csv"})
    assert a != b
