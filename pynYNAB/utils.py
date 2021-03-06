import time

def rate_limited(maxpersecond):
    minInterval = 1.0 / float(maxpersecond)

    def decorate(func):
        lastTimeCalled = [0.0]

        def rateLimitedFunction(*args, **kargs):
            elapsed = time.clock() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait > 0:
                time.sleep(leftToWait)
            ret = func(*args, **kargs)
            lastTimeCalled[0] = time.clock()
            return ret

        return rateLimitedFunction

    return decorate


def chunk(iterable, chunk_size):
    """Generate sequences of `chunk_size` elements from `iterable`."""
    iterable = iter(iterable)
    while True:
        current_chunk = []
        try:
            for _ in range(chunk_size):
                current_chunk.append(next(iterable))
            yield current_chunk
        except StopIteration:
            if current_chunk:
                yield current_chunk
            break


# http://stackoverflow.com/q/10480806/1685379
def equal_dicts(a, b, ignore_keys):
    ka = set(a).difference(ignore_keys)
    kb = set(b).difference(ignore_keys)
    return ka == kb and all(a[k] == b[k] for k in ka)
