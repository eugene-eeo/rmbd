from rmbd.service import normalize, get_outdated


def test_normalize():
    assert normalize(('localhost', 8000)) == ('127.0.0.1', 8000)


def test_get_outdated_empty():
    acks = {}
    times = {'one': 1}
    assert list(get_outdated(acks, times)) == ['one']


def test_get_outdated_lesser():
    acks = {'one': 1, 'two': 0}
    times = {'one': 2}
    assert list(get_outdated(acks, times)) == ['one']
