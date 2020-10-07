# kuqueue
[![Build Status](https://travis-ci.org/yehonatanz/kuqueue.svg?branch=main)](https://travis-ci.org/yehonatanz/kuqueue)
[![codecov](https://codecov.io/gh/yehonatanz/kuqueue/branch/main/graph/badge.svg?token=01O6IAXMR2)](https://codecov.io/gh/yehonatanz/kuqueue)
[![Maintainability](https://api.codeclimate.com/v1/badges/58887c887dd7298f0d55/maintainability)](https://codeclimate.com/github/yehonatanz/kuqueue/maintainability)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI version](https://badge.fury.io/py/kuqueue.svg)](https://badge.fury.io/py/kuqueue)

A lightweight, pythonic wrapper around [pyrsmq](https://github.com/mlasevich/PyRSMQ) to expose MQ semantics over vanilla redis

Continuously tested against a recent redis instance and `python>=3.8`

### Install
```bash
pip install kuqueue
```

For development, clone this repo and run `make install`.

### Usage example
```python
from redis import StrictRedis
from kuqueue import create_kuqueue

redis: StrictRedis
kq = create_kuqueue(redis, namespace="your-app-name", qname="name-of-your-queue", default_job_timeout=30)
kq.create()          # ensures the queue exists in your redis
kq.push(b"message")  # push message with raw bytes data
msg = kq.pull()      # pull a message from the queue, blocking
...                  # do some some work
kq.ack(msg.id)       # acknowledge the message, delete it from the queue
```
