Building Scilab to GSoC
###################################

:date: 2011-04-28
:tags: gsoc
:category: programming


My first task was build Scilab project. It is a huge project, and first time I did it I really didn't know how to do it. I just tried to build, checked the error message `"some lib not found"`, installed that lib, tried to build again and again... dozen of times.

After that, of course I researched about how to build it in a better way. It is really easy using Ubuntu. First of all, just clone Scilab repository with git. I used YaSp branch, but it works to master too. After checkout, build all dependencies (the trick part I didn't know):

.. code-block:: bash

    $ apt-get build-dep scilab

In scilab directory, just configure and make project:

.. code-block:: bash

    $ ./configure
    $ make

This post looks really simple, but it is my first post during GSoC and solved a big issue to me (build dependencies).