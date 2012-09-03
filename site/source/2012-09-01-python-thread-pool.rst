Python thread pool
##################

:date: 2012-09-01
:tags: python, multithreading
:category: programming

It is just a small note about a hidden-ish Python feature. Looking for a thread pool solution, I found the threading module has no support to it.

The most common answers talk about `pythonthreadpool library <http://code.google.com/p/pythonthreadpool/>`_ or `some ActiveState cookbook recipe <http://code.activestate.com/recipes/302746-simplest-useful-i-hope-thread-pool-example/>`_. I'm pretty sure it solves the problem, but that is not how Python should work.

If you take a look at ``multiprocessing.dummy`` module, you will find it has a Pool implementation using the ``threading`` module. I don't know why it is not properly documented, but it replicates multiprocessing pool, so that is exactly what I need.

.. code-block:: python

    from multiprocessing.dummy import Pool

    def f(x):
        # run something cool here
        return x ** 10

    pool = Pool(processes=4)
    result = pool.map(f, range(10))
    print result


Check `multiprocessing.Pool docs <http://docs.python.org/library/multiprocessing.html#module-multiprocessing.pool>`_.
