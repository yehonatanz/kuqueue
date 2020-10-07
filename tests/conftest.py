import pytest
from redis import StrictRedis

from kuqueue import Kuqueue, create_kuqueue


@pytest.fixture
def redis_client(docker_ip: str, docker_services) -> StrictRedis:
    rd = StrictRedis(docker_ip, docker_services.port_for("redis", 6379))
    docker_services.wait_until_responsive(timeout=5, pause=0.1, check=rd.ping)
    rd.flushall()
    return rd


@pytest.fixture
def namespace() -> str:
    return "namespace"


@pytest.fixture
def qname() -> str:
    return "qname"


@pytest.fixture
def job_timeout() -> float:
    return 0.2


@pytest.fixture
def kq(
    redis_client: StrictRedis, namespace: str, qname: str, job_timeout: float
) -> Kuqueue:
    kq = create_kuqueue(
        redis_client,
        namespace=namespace,
        qname=qname,
        default_job_timeout=job_timeout,
    )
    kq.create()
    return kq
