Title: Faster Django migrations with django-migrations-ci
Date: 2023-01-09
Category: programming
Tags: python, django

Django migrations are really slow. It is an [open issue](https://code.djangoproject.com/ticket/29898) for years.
It was even an [Google Summer of Code proposal](https://gist.github.com/aryan9600/b1c2eaf445006c17e02e7677cf1098d5).

For small projects, it take some seconds to run all your migrations and it is fine. A few developers
can work on it for a long time. For a large project, it is not that simple.

Our largest project today has 273 Django models and did ~1000 migrations in 4 years. Sometimes it
takes 15 minutes on CI, even with a lot of optimizations. Django `squashmigrations` command do
optimizations, but could be a lot better. After a lot of squashes, it's still slow.

It was really bad for us, CI failed a lot because of timeouts or random postgres failures after
some time trying to always migrate.

We tried some things to improve our CI pipeline.

## Do not migrate on CI

A common advice to improve this time is to not run migrations on CI. It is fast.

You can override the [`MIGRATIONS_MODULES`](https://docs.djangoproject.com/en/4.1/ref/settings/#std-setting-MIGRATION_MODULES) for testing:

```python
MIGRATION_MODULES = {app.rsplit(".")[-1]: None for app in INSTALLED_APPS}
```

It is not really safe, because now you run migrations only on deployments, which is risky.
Large projects have data migrations, migration bugs and other issues that you want to discover
before production. So we added another stage to run migrations and our problem was back.

## Reuse database

In the past [I had to hack pytest-django setup to run less migrations](/2021/03/faster-parallel-pytest-django.html).
This was useful to know how to separate migrations and test steps.

I changed our pipeline to dump the migrated database to a SQL file and cached it on GitLab CI.

Some old code examples from our CI:

```bash
# Don't try to copy it, please!
if [ -f $CI_PROJECT_DIR/djangomigrations.sql ]; then
    psql -h $DB_HOST -U $POSTGRES_USER -c "CREATE DATABASE $DB_NAME;"
    pg_restore -h $DB_HOST -U $POSTGRES_USER -d $DB_NAME $CI_PROJECT_DIR/djangomigrations.sql
else
    time ./manage.py setup_test_db
    pg_dump -F c -h $DB_HOST -U $POSTGRES_USER $DB_NAME > $CI_PROJECT_DIR/djangomigrations.sql
fi
time ./manage.py clone_test_db
```

Commands `setup_test_db` and `clone_test_db` were just a few lines of Python code, but I'll not paste it here.

```yaml
# GitLab CI cache work this way.
cache:
  key:
    files:
      - "requirements.txt"
      - "*/migrations/*.py"
  paths:
    - djangomigrations.sql
  when: always
```

Perfect! Running a migration state that already ran in the past, GitLab CI give me an
SQL file with this state and I restore it to my database. It took our database migrations from
minutes to just a few seconds. Works for me!

## django-migrations-ci

I went to DjangoCon US to [talk about django-qserializer](https://2022.djangocon.us/talks/django-from-queryset-to-serialization/). There I had some conversations about how migrations are slow.
More people had the same issue, so I started [django-migrations-ci](https://github.com/buserbrasil/django-migrations-ci)
during sprint days of the event.

Using this module, it is just one extra command to setup your test database:

```python
./manage.py migrateci
./manage.py test --keepdb
```

Following my original idea, it started using CI caching to provide a storage layer.

I implemented it to sqlite3, mysql and postgres. Never tried to implement for oracle, but it is easy to add
other databases. Also, I documented how to integrate it with GitHub Actions and GitLab CI.

## Partial caching

After this initial sprint, I replaced the CI caching with a custom storage, easy to integrate
with anything [`django-storages`](https://django-storages.readthedocs.io/en/latest/) support.

I did that to support partial migrations. It was impossible to do it with CI caching, because they don't have
an API to easily choose the cache I want.

When a new migration is added, there is no migration state cached, so all migrations are processed
again. To fix this use case, I wanted to get a previous state, restore from it and run only new
migrations, which is reasonably fast.

## Use it

Now I can say it is easy to reuse my solution and it really adds value to any project where
your migrations take more than a few seconds.

Install it, configure an external storage and add a command to your CI scripts.

```python
from storages.backends.s3boto3 import S3Boto3Storage

class MigrateCIStorage(S3Boto3Storage):
    bucket_name = "mybucket-migrateci-cache"
    region_name = "us-east-1"
```

```shell
$ ./manage.py migrateci --storage-class path.to.MigrateCIStorage
```
