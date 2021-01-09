Honeycomb Django tricks
#######################

:date: 2021-01-10 08:00
:tags: python, django, honeycomb
:category: programming

`Honeycomb <https://www.honeycomb.io/>`_ is the observability tool we use everyday at `Buser <https://www.buser.com.br/>`_. They help us tracking application bottlenecks, slow database queries, slow requests, requests with too many queries and much more.

Their automatic instrumentation with `beeline lib <https://docs.honeycomb.io/getting-data-in/python/beeline/>`_ is a good start, but at some point we had to extend the default behaviour.

Custom request data
===================

We extended the ``HoneyMiddleware`` and changed ``settings.py MIDDLEWARE`` to use our custom middleware because we wanted to track differences between logged and anonymous users.

.. code-block:: python

    from beeline.middleware.django import HoneyMiddleware

    class HoneycombMiddleware(HoneyMiddleware):
        def get_context_from_request(self, request):
            context = super().get_context_from_request(request)
            if request.user.is_authenticated:
                context['request.user.id'] = request.user.id
            return context

We could add ``context['request.user.is_authenticated']`` too, but we did that with a derived column ``EXISTS($"request.user.id")`` in Honeycomb side.

Trace sampling
==============

Honeycomb limits are really friendly, **even for their free plan**, but our traffic increased 5x in 2020 and we reached our plan limits.

Their ``beeline`` client has a ``sample_rate`` config but it's a dummy implementation, generating imcomplete traces, which is useless to us.

We make the sampling decision at the start of the request, unfortunately it's not possible to decide based on request duration or request status.

.. code-block:: python

    from beeline.middleware.django import HoneyMiddleware

    class HoneycombMiddleware(HoneyMiddleware):
        def __call__(self, request):
            sample_rate = self.get_sample_rate(request)
            sampled = random.random() < 1 / sample_rate
            request.__honeycomb_sampled__ = sampled, sample_rate
            return super().__call__(request)

        def get_sample_rate(self, request):
            # Add logic here to decide based on path or other request info.
            return 10


Now, to sample based on this ``__honeycomb_sampled__`` info, beeline need a sampler hook.

.. code-block:: python

    import beeline

    def sampler_hook(event):
        # The get_request is not Django built-in.
        # Check django-middleware-global-request project.
        request = get_request()

        # Ignore when we don't have a request.
        if not request:
            return False, 0

        return request.__honeycomb_sampled__


    beeline.init(sampler_hook=sampler_hook)


Request based sampling
======================

Instead of a fixed sample rate, we have it configured by path and by domain to get better results. Our implementation use Django settings,
but it is easy to start handling just special cases.

.. code-block:: python

    def get_sample_rate(self, request):
        if request.get_host() == 'admin.example.com':
            # Always trace admin domain, it has low volume but lots of slow batch requests.
            return 1
        if request.path == '/search':
            # Reduce high volume path sampling.
            return 80

        return 10


Celery
======

Our project ran only with Django integration for almost a year, focused on critical requests optimizations. We had to offload lots of application work to Celery to handle some bottlenecks, but after that we created a huge blindspot in the stack.

Celery instrumentation
----------------------

Again, beeline has a nice `Celery base implementation <https://docs.honeycomb.io/getting-data-in/python/beeline/#celery>`_, but it doesn't handle sampling well and don't
instrument Django database queries. 

Maybe it's a small bug, based on our use, Celery queue name is in ``delivery_info['routing_key']`` instead of ``delivery_info['exchange']``. We decided to log
both values to not lose useful data.

I reused ideas from their `middleware <https://github.com/honeycombio/beeline-python/blob/2ab8dea5d195096755199ac9badfe671f408bb9d/beeline/middleware/django/__init__.py#L155-L159>`_.

.. code-block:: python

    from contextlib import ExitStack

    from beeline.middleware.django import HoneyDBWrapper
    from celery.signals import task_prerun, task_postrun
    from django.db import connections

    @task_prerun.connect
    def setup_django_db(task):
        task.request._exit_stack = ExitStack()
        db_wrapper = HoneyDBWrapper()
        for connection in connections.all():
            task.request._exit_stack.enter_context(connection.execute_wrapper(db_wrapper))

    @task_postrun.connect
    def teardown_django_db(task):
        task.request._exit_stack.close()


Celery sampling
---------------

Celery sampling was a challenge, because Celery internals don't have good documentation.

.. code-block:: python

    import random
    import celery

    from celery.signals import task_prerun

    def sampler_hook(event):
        return celery.current_app.current_worker_task.request.__honeycomb_sampled__

    def sampling(sample_rate):
        sampled = random.random() < 1 / sample_rate
        return sampled, sample_rate

    @task_prerun.connect
    def setup_sampling(task):
        task.request.__honeycomb_sampled__ = sampling()

The ``beeline.init`` now need a ``sampler_hook``.

.. code-block:: python
    
    import beeline
    from celery.signals import worker_process_init

    @worker_process_init.connect
    def initialize_honeycomb(**kwargs):
        beeline.init(sampler_hook=sampler_hook)


uWSGI integration
=================

`uWSGI integrations <https://docs.honeycomb.io/getting-data-in/python/beeline/#uwsgi>`_ was probably our first small issue.

Package `uwsgidecorators` is available only inside uwsgi context and we wanted to run in development too. The `_init_beeline` in the code is the docs `init_beeline`. When it's not in uwsgi context, it setup beeline too.

.. code-block:: python

    def init_beeline():
        try:
            import uwsgidecorators
        except ImportError:
            _init_beeline()
        else:
            uwsgidecorators.postfork(_init_beeline)
