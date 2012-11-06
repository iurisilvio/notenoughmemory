Wordpress: "You do not have sufficient permissions to access this page."
########################################################################

:date: 2012-11-06
:tags: wordpress, noob
:category: issue

After I migrate my blog to my production environment, I was not able to login in ``/wp-admin/``, receiving a quick message even in debug mode:

``"You do not have sufficient permissions to access this page."``

Ok, I just copied my database and my code, just changing configurations. `Google have a lot of results about this issue <https://www.google.com/webhpq=wordpress+%22You+do+not+have+sufficient+permissions+to+access+this+page.%22&oq=wordpress+%22You+do+not+have+sufficient+permissions+to+access+this+page.%22>`_, but it is not a simple problem. This message have a lot of meanings, maybe you just don't have access to database.

I used almost a day reading Google results, but no one solved my problem. Of course, after I decided to stop, I get my ``wp-config.php`` files (development and production) and diffed then (`<http://www.quickdiff.com>`_ is awesome).

.. code-block:: diff

    - $table_prefix = 'wpProject_';
    + $table_prefix = 'wpproject_';

If you know a bit about MySQL, you know tables are not case sensitive in Windows. Wordpress don't care about that and don't give you any hint. So, if you found this post because you had a similar problem, go check your configurations.

Just to make it obvious to anyone trying to solve the problem: **TABLE PREFIX IS CASE SENSITIVE**. Of course, maybe it is not the answer you need, because the "error message" does not give you much information.
