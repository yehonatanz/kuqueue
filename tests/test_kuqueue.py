from kuqueue import Kuqueue


def test_one_push_one_pull(kq: Kuqueue) -> None:
    id = kq.push(b"abc\xde")
    msg = kq.pull()
    assert msg.id == id
    assert msg.message == b"abc\xde"
