import time


def ratelimited(maxpersecond):
    minInterval = 1.0 / float(maxpersecond)

    def decorate(func):
        lastTimeCalled = [0.0]

        def rate_limited_function(*args, **kargs):
            elapsed = time.clock() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait > 0:
                time.sleep(leftToWait)
            ret = func(*args, **kargs)
            lastTimeCalled[0] = time.clock()
            return ret

        return rate_limited_function

    return decorate


def chunk(iterable, chunk_size):
    """Generate sequences of `chunk_size` elements from `iterable`."""
    iterable = iter(iterable)
    while True:
        newchunk = []
        try:
            for _ in range(chunk_size):
                newchunk.append(next(iterable))
            yield newchunk
        except StopIteration:
            if newchunk:
                yield newchunk
            break

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

