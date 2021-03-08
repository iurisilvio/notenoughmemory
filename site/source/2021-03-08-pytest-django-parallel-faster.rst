Faster parallel pytest-django
#############################

:date: 2021-03-08 08:00
:tags: python, django, pytest
:category: programming

We at Buser recently migrated from Django unittests to pytest. It is amazing
how much you can improve your tests with pytest.

Unfortunately our CI/CD was really slow after this change.

I discovered parallel ``pytest-django`` do their setup different than Django
unittests. Django create a template database and copy it to every test node,
``pytest-django`` create one database per node. Running this setup with migrations
took more than 2 minutes just to have the database created.

This is a problem mostly for CI/CD, because local you can run with ``--reuse-db``
and the overhead is minimal, only when you have database migrations.

I wanted to fix this in ``pytest-django``, but I discovered it is difficult because
pytest-xdist don't have a global setup and teardown.

Now I have a small hack, working great so far. This is the script running our
tests:

.. code-block:: shell

    ./manage.py shell -c "
    from django.test.utils import setup_databases
    from xdist.plugin import pytest_xdist_auto_num_workers
    setup_databases(verbosity=True, interactive=False, parallel=pytest_xdist_auto_num_workers())
    "
    pytest --reuse-db -n auto

Django unittests generate names like ``test_yourdb_1``, ``test_yourdb_2`` and
``pytest-django`` generate names like ``test_yourdb_gw0``, ``test_yourdb_gw1``, their
names don't match, I had to make a fixture to monkey patch their behaviors.

.. code-block:: python

    from pytest_django.fixtures import _set_suffix_to_test_databases
    from pytest_django.lazy_django import skip_if_no_django

    # Original code: https://github.com/pytest-dev/pytest-django/blob/bd2ae62968aaf97c6efc7e02ff77ba6160865435/pytest_django/fixtures.py#L46
    @pytest.fixture(scope="session")
    def django_db_modify_db_settings_xdist_suffix(request):
        skip_if_no_django()

        xdist_suffix = getattr(request.config, "workerinput", {}).get("workerid")
        if xdist_suffix:
            # 'gw0' -> '1', 'gw1' -> '2', ...
            suffix = str(int(xdist_suffix.replace('gw', '')) + 1)
            _set_suffix_to_test_databases(suffix=suffix)

I tried to make a pull request to ``pytest-django``, but this issue exists
because pytest-xdist don't have hooks to run before and after every node.
