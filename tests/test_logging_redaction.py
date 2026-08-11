from app.logging_config import scrub_event


def test_redaction_covers_bound_context_not_just_payload() -> None:
    record = scrub_event(
        None,
        "info",
        {
            "event": "request_received",
            "session_id": "student@vinuni.edu.vn",
            "payload": {"message_preview": "Call 090 123 4567"},
        },
    )

    assert record["session_id"] == "[REDACTED_EMAIL]"
    assert record["payload"]["message_preview"] == "Call [REDACTED_PHONE_VN]"
