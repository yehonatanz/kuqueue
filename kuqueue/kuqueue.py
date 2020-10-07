from __future__ import annotations

import datetime as dt
import time
from dataclasses import dataclass
from typing import Optional, Union, cast, overload

from redis import StrictRedis
from rsmq import RedisSMQ
from rsmq.cmd import NoMessageInQueue, QueueAlreadyExists

MessageData = bytes
MessageId = bytes
Number = Union[int, float]


def create_rsmq(
    client: StrictRedis, namespace: str, qname: str, default_job_timeout: Number
) -> RedisSMQ:
    return RedisSMQ(client=client, ns=namespace, qname=qname, vt=default_job_timeout)


def create_kuqueue(
    client: StrictRedis, namespace: str, qname: str, default_job_timeout: Number
) -> Kuqueue:
    return Kuqueue(create_rsmq(client, namespace, qname, default_job_timeout))


@dataclass(frozen=True)
class Message:
    id: MessageId
    message: MessageData
    rc: int
    ts: int

    @property
    def timestamp(self) -> dt.datetime:
        """
        Creation time of the message
        """
        return dt.datetime.fromtimestamp(self.ts / 1000.0)


def _clamp(value: Number, low: Number, high: Number) -> Number:
    return max([min([value, high]), low])


@dataclass
class Kuqueue:
    rsmq: RedisSMQ

    def push(self, message: MessageData) -> MessageId:
        """
        Pushes a new message to the queue.
        Returns its auto-generated ID.
        """
        return cast(str, self.rsmq.sendMessage(message=message).execute()).encode(
            "ascii"
        )

    @overload
    def pull(
        self, pull_timeout: Number, job_timeout: Optional[Number] = None
    ) -> Optional[Message]:
        ...

    @overload
    def pull(
        self, pull_timeout: None = None, job_timeout: Optional[Number] = None
    ) -> Message:
        ...

    def pull(
        self,
        pull_timeout: Optional[Number] = None,
        job_timeout: Optional[Number] = None,
    ) -> Optional[Message]:
        """
        Pulls a message from the queue.
        If the queue is empty, blocks for `pull_timeout` seconds (forever if None).
        The message will expire and return to the queue
        if not acked within `job_timeout` seconds (or the default job timeout if None).
        """
        deadline = None if pull_timeout is None else (time.time() + pull_timeout)
        while deadline is None or time.time() < deadline:
            try:
                message = self.rsmq.receiveMessage(vt=job_timeout).execute()
            except NoMessageInQueue:
                sleep = 0.05 if deadline is None else (time.time() - deadline) / 10
                time.sleep(_clamp(sleep, 0.02, 0.1))
            else:
                message["ts"] = int(message["ts"])
                return Message(**message)
        return None

    def ack(self, id: MessageId) -> bool:
        """
        Acks the message and deletes it from the queue.
        Return whether the message existed.
        """
        return cast(bool, self.rsmq.deleteMessage(id=id).execute())

    def create(self, exists_ok: bool = True) -> bool:
        """
        Try to creates the queue and returns whether it was created.
        If exists_ok is falsy, raises an exception when the queue already exists.
        """
        try:
            self.rsmq.createQueue().execute()
        except QueueAlreadyExists:
            if exists_ok:
                return False
            else:
                raise
        else:
            return True
