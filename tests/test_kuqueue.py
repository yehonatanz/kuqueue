from __future__ import annotations

import time

from kuqueue import Kuqueue


def test_one_push_one_pull(kq: Kuqueue) -> None:
    id = kq.push(b"abc\xde")
    msg = kq.pull()
    assert msg.id == id
    assert msg.message == b"abc\xde"


def test_pull_fails_if_nothing_in_queue(kq: Kuqueue) -> None:
    assert kq.pull(0.2) is None


def test_cannot_pull_already_pulled_messages(kq: Kuqueue) -> None:
    kq.push(b"00")
    assert kq.pull() is not None
    assert kq.pull(0.2) is None


def test_can_pull_message_if_timeout_has_passed(kq: Kuqueue, job_timeout: int) -> None:
    id = kq.push(b"abc\xde")
    m1 = kq.pull()
    time.sleep(job_timeout)
    m2 = kq.pull()
    assert m1.id == m2.id == id
    assert m1.message == m2.message == b"abc\xde"
    assert m1.timestamp == m2.timestamp
    assert m1.rc == 1
    assert m2.rc == 2
