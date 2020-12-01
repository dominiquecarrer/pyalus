#!/usr/bin/env python3
def chunk_1D(xslice, chunksize):
    """ Take a xslice object, with step==1, and chunk it into parts of the same size. See chunk_2D for examples. """

    if chunksize is None:
        return [xslice]

    if not(xslice.step is None) and xslice.step != 1:
        raise NotImplementedError(f'Config error, cannot chunk xslice {xslice}')

    lenght = xslice.stop - xslice.start
    n = int(lenght / chunksize)
    outlist = [slice(xslice.start + s * chunksize, xslice.start + s * chunksize + chunksize) for s in range(0,n)]
    rest = lenght - n * chunksize
    if rest:
        outlist.append(slice(xslice.stop - rest, xslice.stop))
    return outlist


def chunk_2D(xslice, yslice, xchunksize, ychunksize):
    """
    Take two xslices objects, with step==1, and chunk them into parts of the same size

    Examples :

    >>> def test_chunks(xslice, yslice, xchunksize, ychunksize):
    ...    print(xslice, yslice, xchunksize, ychunksize)
    ...    print(chunk_1D(xslice, xchunksize))
    ...    print(chunk_1D(yslice, ychunksize))
    ...    print(chunk_2D(xslice, yslice, xchunksize, ychunksize))
    >>> test_chunks(xslice = slice(0,29), yslice = slice(0,19),  xchunksize=10,ychunksize=10)
    slice(0, 29, None) slice(0, 19, None) 10 10
    [slice(0, 10, None), slice(10, 20, None), slice(20, 29, None)]
    [slice(0, 10, None), slice(10, 19, None)]
    [(slice(0, 10, None), slice(0, 10, None)), (slice(0, 10, None), slice(10, 19, None)), (slice(10, 20, None), slice(0, 10, None)), (slice(10, 20, None), slice(10, 19, None)), (slice(20, 29, None), slice(0, 10, None)), (slice(20, 29, None), slice(10, 19, None))]

    >>> test_chunks(xslice = slice(0,30), yslice = slice(0,20), xchunksize=10,ychunksize=10)
    slice(0, 30, None) slice(0, 20, None) 10 10
    [slice(0, 10, None), slice(10, 20, None), slice(20, 30, None)]
    [slice(0, 10, None), slice(10, 20, None)]
    [(slice(0, 10, None), slice(0, 10, None)), (slice(0, 10, None), slice(10, 20, None)), (slice(10, 20, None), slice(0, 10, None)), (slice(10, 20, None), slice(10, 20, None)), (slice(20, 30, None), slice(0, 10, None)), (slice(20, 30, None), slice(10, 20, None))]

    >>> test_chunks(xslice = slice(0,40), yslice = slice(0,60), xchunksize=20,ychunksize=10)
    slice(0, 40, None) slice(0, 60, None) 20 10
    [slice(0, 20, None), slice(20, 40, None)]
    [slice(0, 10, None), slice(10, 20, None), slice(20, 30, None), slice(30, 40, None), slice(40, 50, None), slice(50, 60, None)]
    [(slice(0, 20, None), slice(0, 10, None)), (slice(0, 20, None), slice(10, 20, None)), (slice(0, 20, None), slice(20, 30, None)), (slice(0, 20, None), slice(30, 40, None)), (slice(0, 20, None), slice(40, 50, None)), (slice(0, 20, None), slice(50, 60, None)), (slice(20, 40, None), slice(0, 10, None)), (slice(20, 40, None), slice(10, 20, None)), (slice(20, 40, None), slice(20, 30, None)), (slice(20, 40, None), slice(30, 40, None)), (slice(20, 40, None), slice(40, 50, None)), (slice(20, 40, None), slice(50, 60, None))]

    >>> test_chunks(xslice = slice(0,40), yslice = slice(0,60), xchunksize=20,ychunksize=30) 
    slice(0, 40, None) slice(0, 60, None) 20 30
    [slice(0, 20, None), slice(20, 40, None)]
    [slice(0, 30, None), slice(30, 60, None)]
    [(slice(0, 20, None), slice(0, 30, None)), (slice(0, 20, None), slice(30, 60, None)), (slice(20, 40, None), slice(0, 30, None)), (slice(20, 40, None), slice(30, 60, None))]

    """
    xlist = chunk_1D(xslice, xchunksize)
    ylist = chunk_1D(yslice, ychunksize)
    outlist = []
    for xs in xlist:
        for ys in ylist:
            outlist.append((xs,ys))
    return outlist


if __name__ == "__main__":
    # this doctest allows some automated testing of the funcions based on
    # the comments (called docstring) in triple quotes below the function.
    # See https://docs.python.org/2/library/doctest.html fro details.
    import doctest
    doctest.testmod()
