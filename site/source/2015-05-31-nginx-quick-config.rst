Nginx quick configuration
#########################

:date: 2015-05-31
:tags: nginx, cache, load balance
:category: devops

Nginx is an HTTP server with lots of features. The configuration is easy, but maybe you don't even know the feature exist.

I want to present some nginx features and give you some pointers to continue your research.

The basics
==========

The basic usage of nginx is to make the reverse proxy to your application. Nginx listen to port ``80`` waiting for requests and manage
the connections, passing the requests to your upstream application server.

.. code:: nginx

    server {
        server_name www.yoursite.com;
        listen 80;
        location / {
            proxy_pass http://localhost:8080;
        }
    }

The ``proxy_pass`` directive proxy the request as HTTP to your application listening port ``8080``.

You can use ``uwsgi_pass`` to make nginx convert the HTTP to a WSGI request and send it to your WSGI application.

.. code:: nginx

    server {
        server_name www.yoursite.com;
        listen 80;
        location / {
            include uwsgi_params;
            uwsgi_pass localhost:8080;
        }
    }


Most features work for HTTP and uWSGI proxy, with some small configuration changes.


SSL Termination
===============

Nginx terminate the SSL connection and send it to your application as plain HTTP.

.. code:: nginx

    ssl_certificate /opt/ssl/www.yoursite.com.crt;
    ssl_certificate_key /opt/ssl/www.yoursite.com.key;
    server {
        server_name www.yoursite.com;
        listen 443 ssl;
        location / {
            proxy_pass http://localhost:8080;
        }
    }

If you want a HTTPS only website, add another server block to redirect the HTTP traffic to HTTPS.

.. code:: nginx

    server {
        listen 80;
        server_name www.yoursite.com;
        return 301 https://$host$request_uri;
    }

Static files
============

Nginx serve some thousands of static files per second, without hiccups. Do not make your application serve static files, like images and javascripts. Your application is slow, maybe it'll re-render the same asset for each request.

.. code:: nginx

    server {
        server_name www.yoursite.com;
        listen 80;
        root /some/path;
        location /static/ {
            try_files /generated/$uri /cache/$uri @myapp;
        }
        location / {
            try_files $uri @myapp;
        }
        location @myapp {
            include uwsgi_params;
            uwsgi_pass localhost:8080;
        }
    }

The ``try_files`` directive in ``/static/`` block will check ``/some/path/generated/static/`` and ``/some/path/cache/static/`` for your requested file and if it does not exist, send the request to your application.

You can change the last ``try_files`` parameter with ``=404`` to answer with a 404 instead of pass the request to application.

Load balancing
==============

If you want a high available application, nginx can be your load balancer to distribute the load and handle gracefully server failures.

.. code:: nginx

    upstream yourapp {
        server http://localhost:8080 weight=5;
        server http://localhost:8081;
        server http://example.com:8080 backup;
    }
    server {
        server_name www.yoursite.com;
        listen 80;
        location / {
            proxy_pass yourapp;
        }
    }

Nginx send the request to your ``yourapp`` upstream, choosing one server in a weighted round robin way. 5 requests to the first server, 1 request to the second server and so on. If your servers are down, it sends the request to your backup server.

If one server fail to answer or give an HTTP error, nginx send the request to the next server. No additional configuration needed.

Caching
=======

Some pages are almost static and you don't want it rendering all the time. Nginx can help you serving this content. Configure nginx to cache the page for 10 minutes.

.. code:: nginx

    uwsgi_cache_path /tmp/myapp/content/ keys_zone=myapp-content:10m
                     loader_threshold=300 loader_files=200 max_size=100m levels=1:2;
    uwsgi_cache_valid 200 301 302 404 10m;
    uwsgi_cache_key $host$request_uri;

    server {
        server_name www.yoursite.com;
        listen 80;
        location /content/ {
            uwsgi_cache yourcache;
            uwsgi_ignore_headers Set-Cookie;
            uwsgi_hide_header Set-Cookie;
            add_header X-Cache $upstream_cache_status;
            include uwsgi_params;
            uwsgi_pass localhost:8080;
        }
        location / {
            include uwsgi_params;
            uwsgi_pass localhost:8080;
        }
    }


Dynamic upstreams
=================

The commercial subscription has this feature built-in, but you probably don't want one. It costs some thousand dollars per server.

The simple way to do it is update the configuration file, adding/removing upstream servers. The ``nginx reload`` command update the configuration without
downtime.


Conclusion
==========

These snippets are just the basics. Use it to understand how it can help you, but check the docs to learn all the features. Nginx is really powerful and can help you to simplify and improve your system architecture.

Feel free to contact me if you want some help setting up your nginx server. I'm not a system administrator, but I learnt some things about it.
