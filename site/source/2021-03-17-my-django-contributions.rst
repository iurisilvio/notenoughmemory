My Django contributions
#######################

:date: 2021-03-17
:tags: python, django
:category: programming

I started contributing to Django core after a failure in our project.

I had to rename a model attribute without touching our database. The solution
was simple.

.. code-block:: python

    # Simple attribute to rename.
    author = models.ForeignKey('Author')

    # 1. Add db_column param.
    author = models.ForeignKey('Author', db_column='author')

    # 2. Change the attribute name.
    creator = models.ForeignKey('Author', db_column='author')


It was really obvious to me that it should be a noop to database. Even Stack Overflow
`had a response confirming that <https://stackoverflow.com/a/33191630/617395>`_.

The first migration locked our database because it dropped and recreated a constraint.

.. code-block:: sql

    SET CONSTRAINTS "core_book_author_id_eaa1580d_fk_core_author_id" IMMEDIATE;
    ALTER TABLE "core_book" DROP CONSTRAINT "core_book_author_id_eaa1580d_fk_core_author_id";
    ALTER TABLE "core_book" ADD CONSTRAINT "core_book_author_id_eaa1580d_fk_core_author_id"
        FOREIGN KEY ("author_id") REFERENCES "core_author" ("id") DEFERRABLE INITIALLY DEFERRED;

Sad day, but right after that I prepared to run the second step. That time I
checked the generated SQL with ``sqlmigrate`` command and discovered it will
do the same thing again.

To avoid another failure, I did only a ``SeparateDatabaseAndState`` change.
Works great, but Django could do better handling these migrations.

.. code-block:: python

    from django.db import migrations, models

    class Migration(migrations.Migration):
        atomic = False
        dependencies = [
            ('core', '0137_auto_20200227_1304'),
        ]
        operations = [
            migrations.SeparateDatabaseAndState(
                state_operations=[
                    migrations.RenameField(
                        model_name='book', old_name='author', new_name='creator',
                    ),
                ],
                database_operations=[],
            ),
        ]


After that, I checked Django tickets and didn't found anything related. Created
a ticket and implemented two pull requests to fix both steps
`1 <https://code.djangoproject.com/ticket/31825>`_
`2 <https://code.djangoproject.com/ticket/31826>`_.
They were merged and released with Django 3.1.1 after long PR conversations.

Django is a huge codebase and even a minor change like that took me some days,
changing the wrong things in the different wrong ways. I learned a lot and was
able to fix another `migrations ticket <https://code.djangoproject.com/ticket/31831>`_.

Right after these fixes, I upgraded our Django and hit a `recent regression <https://code.djangoproject.com/ticket/31870>`_. It was a quick fix, but lots of
tests written.

When our new intern started, he had an issue with queryset `in_bulk` operation,
because of incomplete docs and it was a `simple commit <https://code.djangoproject.com/ticket/32313>`_
to improve their docs.
