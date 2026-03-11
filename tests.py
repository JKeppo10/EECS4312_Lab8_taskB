import pytest
from solution import EventRegistration, UserStatus, DuplicateRequest, NotFound


# C3, C8, AC1, AC2, EC1, FR1
def test_register_until_capacity_then_waitlist_fifo_positions():
    er = EventRegistration(capacity=2)

    s1 = er.register("u1")
    s2 = er.register("u2")
    s3 = er.register("u3")
    s4 = er.register("u4")

    assert s1 == UserStatus("registered")
    assert s2 == UserStatus("registered")
    assert s3 == UserStatus("waitlisted", 1)
    assert s4 == UserStatus("waitlisted", 2)

    snap = er.snapshot()
    assert snap["registered"] == ["u1", "u2"]
    assert snap["waitlist"] == ["u3", "u4"]


# C1, C3, AC2, AC10, EC1, FR2, FR11
def test_cancel_registered_promotes_earliest_waitlisted_fifo():
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")  # waitlist
    er.register("u3")  # waitlist

    er.cancel("u1")  # should promote u2

    assert er.status("u1") == UserStatus("none")
    assert er.status("u2") == UserStatus("registered")
    assert er.status("u3") == UserStatus("waitlisted", 1)

    snap = er.snapshot()
    assert snap["registered"] == ["u2"]
    assert snap["waitlist"] == ["u3"]


# C5, C11, AC8, FR5, FR14
def test_duplicate_register_raises_for_registered_and_waitlisted():
    er = EventRegistration(capacity=1)
    er.register("u1")
    with pytest.raises(DuplicateRequest):
        er.register("u1")

    er.register("u2")  # waitlisted
    with pytest.raises(DuplicateRequest):
        er.register("u2")


# C1, C3, AC2, EC2
def test_waitlisted_cancel_removes_and_updates_positions():
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")  # waitlist pos1
    er.register("u3")  # waitlist pos2

    er.cancel("u2")    # remove from waitlist

    assert er.status("u2") == UserStatus("none")
    assert er.status("u3") == UserStatus("waitlisted", 1)

    snap = er.snapshot()
    assert snap["registered"] == ["u1"]
    assert snap["waitlist"] == ["u3"]


# EC5, FR25
def test_capacity_zero_all_waitlisted_and_promotion_never_happens():
    er = EventRegistration(capacity=0)
    assert er.register("u1") == UserStatus("waitlisted", 1)
    assert er.register("u2") == UserStatus("waitlisted", 2)

    # No one can ever be registered when capacity=0
    assert er.status("u1") == UserStatus("waitlisted", 1)
    assert er.status("u2") == UserStatus("waitlisted", 2)
    assert er.snapshot()["registered"] == []

    # Cancel unknown should raise NotFound (C11, AC13)
    with pytest.raises(NotFound):
        er.cancel("missing")


# C1, C3, AC1
def test_register_when_capacity_available():
    er = EventRegistration(capacity=3)

    assert er.register("u1") == UserStatus("registered")
    assert er.register("u2") == UserStatus("registered")

    snap = er.snapshot()
    assert snap["registered"] == ["u1", "u2"]
    assert snap["waitlist"] == []


# C3, AC1, AC2
def test_register_beyond_capacity_waitlists_users():
    er = EventRegistration(capacity=2)

    er.register("u1")
    er.register("u2")

    s3 = er.register("u3")

    assert s3 == UserStatus("waitlisted", 1)

    snap = er.snapshot()
    assert snap["registered"] == ["u1", "u2"]
    assert snap["waitlist"] == ["u3"]


# FR5, C5, AC8
def test_reregister_after_cancel():
    er = EventRegistration(capacity=1)

    er.register("u1")
    er.cancel("u1")

    assert er.register("u1") == UserStatus("registered")

    snap = er.snapshot()
    assert snap["registered"] == ["u1"]
    assert snap["waitlist"] == []


# C11, AC13
def test_status_for_unknown_user():
    er = EventRegistration(capacity=2)

    assert er.status("ghost") == UserStatus("none")


# C1, C3, AC2, EC1
def test_waitlist_promotion_fifo_multiple():
    er = EventRegistration(capacity=1)

    er.register("u1")
    er.register("u2")
    er.register("u3")

    er.cancel("u1")

    assert er.status("u2") == UserStatus("registered")
    assert er.status("u3") == UserStatus("waitlisted", 1)

    er.cancel("u2")

    assert er.status("u3") == UserStatus("registered")


# C3, C5, AC8
def test_reregister_after_cancel_does_not_raise():
    er = EventRegistration(capacity=1)

    er.register("u1")
    er.cancel("u1")

    # should NOT raise DuplicateRequest
    status = er.register("u1")

    assert status == UserStatus("registered")


# C3, C8, AC7, EC1
def test_multiple_promotions_fifo_order():
    er = EventRegistration(capacity=1)

    er.register("u1")
    er.register("u2")
    er.register("u3")

    er.cancel("u1")

    assert er.status("u2") == UserStatus("registered")
    assert er.status("u3") == UserStatus("waitlisted", 1)

    er.cancel("u2")

    assert er.status("u3") == UserStatus("registered")


# FR14, C5, AC11, EC2
def test_user_not_in_both_lists():
    er = EventRegistration(capacity=1)

    er.register("u1")
    er.register("u2")

    registered = set(er.snapshot()["registered"])
    waitlist = set(er.snapshot()["waitlist"])

    assert registered.isdisjoint(waitlist)


# FR3, C11
def test_invalid_user_id_raises():
    er = EventRegistration(capacity=2)

    with pytest.raises(ValueError):
        er.register("invalid_user!")  # special character


# FR25, EC5, AC13
def test_dynamic_capacity_increase_promotes_waitlist():
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")  # waitlisted
    er.register("u3")  # waitlisted

    er.set_capacity(3)  # increase capacity

    assert er.status("u2") == UserStatus("registered")
    assert er.status("u3") == UserStatus("registered")
    assert er.snapshot()["waitlist"] == []


# C4, AC6
def test_notification_throttling_respected(monkeypatch):
    er = EventRegistration(capacity=1, notification_window=2)

    er.register("u1")
    er.register("u2")  # waitlisted
    first_messages = list(er.messages)

    # Register u2 again quickly to attempt duplicate message
    with pytest.raises(DuplicateRequest):
        er.register("u2")
    second_messages = list(er.messages)

    # No new messages should be added for the duplicate attempt
    assert first_messages == second_messages


# EC6, C12, FR15
def test_simultaneous_register_and_cancel_consistent_state():
    er = EventRegistration(capacity=1)

    er.register("u1")
    # cancel and register same user sequentially
    er.cancel("u1")
    s = er.register("u1")

    assert s == UserStatus("registered")
    snap = er.snapshot()
    assert snap["registered"] == ["u1"]
    assert snap["waitlist"] == []
