Title: Django Sessions to cache
Date: 2021-04-28
Category: programming
Tags: python, django

Django sessions works great since the begining, you can do a site with them and
never really understand how sessions works, but you can't scale to thousands of
simultaneous users writing all your sessions to database. The database can be a
huge bottleneck here and you should remove all unnecessary reading and writing.

Fortunately, Django has good alternatives almost built-in. They provide other
session backends, like `cached_db` and `cache`. It has [extensive docs](https://docs.djangoproject.com/en/3.2/topics/http/sessions/), but I had some issues migrating to cache backend.

Doing that in production means current sessions can't be removed during migration.

I decided for the easy path:

1. Change `SESSION_ENGINE='django.contrib.sessions.backends.cached_db'`.
1. Wait some days to have all useful sessions cached. More than `SESSION_COOKIE_AGE` was
enough to me.
1. Change `SESSION_ENGINE='django.contrib.sessions.backends.cache'`.

It doesn't work.

Both session engines define keys as `key_prefix + session_id`, with different
prefixes. [Django do that to avoid namespace clash](https://github.com/django/django/blob/ca9872905559026af82000e46cde6f7dedc897b6/docs/topics/http/sessions.txt#L827-L834
).
It is a sane default, but I want namespace clash to simplify the migration path.

I can define custom session backends with the key prefixes I want. Each one
should be a file because `SESSION_ENGINE` must be a module with a `SessionStore`.

```python
# base.py
class BaseSessionStoreMixin:
    cache_key_prefix = 'busersessionstore'
```

```python
# cache.py
from django.contrib.sessions.backends import cache

from . import base


class SessionStore(base.BaseSessionStoreMixin, cache.SessionStore):
    pass
```

```python
# cached_db.py
from django.contrib.sessions.backends import cached_db

from . import base


class SessionStore(base.BaseSessionStoreMixin, cached_db.SessionStore):
    pass
```

Now I can do the same thing, using my session engines.

1. Change `SESSION_ENGINE='myproject.sessions.cached_db'`.
1. Wait some days to have all useful sessions cached. More than `SESSION_COOKIE_AGE` was
enough to me.
1. Change `SESSION_ENGINE='myproject.sessions.cache'`.

It works!

Just as disclaimer, memcached don't have a good way to make this data durable.
If memcached node restart, all data is lost. We're using redis with replicas,
so I lose all data only if all nodes explode at the same time.
