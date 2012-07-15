Google App Engine in a Bottle
#############################

:date: 2011-05-29
:tags: bottle, appengine
:category: programming

First of all, you must know `bottle <http://bottlepy.org>`_ and `Google App Engine <https://developers.google.com/appengine>`_. Both are awesome tools to any web project. They together make both even easier to use. This integration is easy but isn't too much documented.

Add ``bottle.py`` to your source folder and create a ``helloworld.py`` file with this content:

.. code:: python

    from google.appengine.ext.webapp import util
    import bottle
    from bottle import route

    @route(["/", "/:name"])
    def hello(name="World"):
        return "Hello %s" % name

    def main():
        bottle.debug(True)
        bottle.run(server='gae')
  
    if __name__ == "__main__":
        main()
   
In your ``app.yaml``, just send everything to your ``helloworld.py`` app:

.. code-block:: yaml

    application: sample-app
    version: 1
    runtime: python
    api_version: 1

    handlers:
      - url: /.*
      script: helloworld.py


Run ``dev_appserver.py`` to test (you already know how to do it if you read Getting Started).

It works nice with last Bottle (v0.9.1). All Google App Engine features are decoupled from webapp, so you can use database, user authentication and others with Bottle.
