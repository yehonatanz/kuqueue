from __future__ import annotations

import time

import pytest
from redis import StrictRedis

from kuqueue import Kuqueue, QueueAlreadyExists


def test_one_push_one_pull(kq: Kuqueue) -> None:
    id = kq.push(b"abc\xde")
    msg = kq.pull()
    assert msg.id == id
    assert msg.message == b"abc\xde"


def test_pull_fails_if_nothing_in_queue(kq: Kuqueue) -> None:
    assert kq.pull(0.2) is None


def test_cannot_pull_already_pulled_messages(kq: Kuqueue, job_timeout: float) -> None:
    kq.push(b"00")
    assert kq.pull() is not None
    assert kq.pull(job_timeout * 0.95) is None


def test_can_pull_message_if_timeout_has_passed(
    kq: Kuqueue, job_timeout: float
) -> None:
    id = kq.push(b"abc\xde")
    m1 = kq.pull()
    time.sleep(job_timeout * 1.05)
    m2 = kq.pull()
    assert m1.id == m2.id == id
    assert m1.message == m2.message == b"abc\xde"
    assert m1.timestamp == m2.timestamp
    assert m1.rc == 1
    assert m2.rc == 2


def test_cannot_pull_acked_message_even_if_timeout_has_passed(
    kq: Kuqueue, job_timeout: float
) -> None:
    id = kq.push(b"abc\xde")
    msg = kq.pull()
    assert msg.id == id
    assert kq.ack(id) is True
    time.sleep(job_timeout * 1.05)
    assert kq.pull(0.2) is None


def test_create_queue_fails_if_queue_exists(kq: Kuqueue) -> None:
    with pytest.raises(QueueAlreadyExists):
        kq.create(exists_ok=False)


def test_create_queue_succeeds_if_queue_exists(kq: Kuqueue) -> None:
    assert kq.create() is False


def test_delete_queue(kq: Kuqueue, redis_client: StrictRedis):
    assert kq.delete() is True
    assert redis_client.keys() == []
    assert kq.delete() is False
    assert redis_client.keys() == []
