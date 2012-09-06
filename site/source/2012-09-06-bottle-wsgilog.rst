Bottle wsgilog
##############

:date: 2012-09-06
:tags: python, bottle
:category: programming

Python has awesome tools for logging, including standard logging module. Also, through WSGI protocol we have the wsgilog middleware. Using it is easy with any Python web framework.

You can easily integrate it in bottle environment.

.. code-block:: python

    import bottle
    from wsgilog import log

    app = bottle.Bottle(catchall=False)
    logger_middleware = log(tohtml=True, tofile='wsgi.log', tostream=True, toprint=True)

    @app.route('/')
    def index():
        print 'STDOUT is logged.'
        bottle.request.environ['wsgilog.logger'].info('This information is logged.')
        # Exception will be logged and sent to the browser formatted as HTML only if app catchall=False.
        raise Exception()

    app = logger_middleware(app)

    bottle.run(app)


If you need to log each call to bottle, you can use `application hooks <http://bottlepy.org/docs/dev/api.html#bottle.Bottle.hook>`_.

.. code-block:: python

    @app.hook('before_request')
    def before_request():
        logger = bottle.request.environ['wsgilog.logger']
        logger.info('before_request %s %s' % (request.method, request.path))

    @app.hook('after_request')
    def after_request():
        logger = bottle.request.environ['wsgilog.logger']
        logger.info('after_request %s %s' % (request.method, request.path))
