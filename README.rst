====================
Django-Dynamic-Admin
====================

Create dynamic models from Django administration (with migration support).


Quick start
-----------

1. Install django-dynamic-admin package in your Django project::

    pip install django-dynamic-admin

2. Add "django-dynamic-admin" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'polymorphic'
        'dynamicadmin',
    ]

3. Run `python manage.py migrate` to create the base models.

4. See https://github.com/seht/dynamicadmin-example-project for example usage.

5. Visit http://127.0.0.1:8000/admin/ to create dynamic models from Django administration.


Adding new Field types
----------------------

Create new field types by extending `dynamicadmin.models.Field`


Adding new Content types
------------------------

Create new content types by extending `dynamicadmin.models.Bundle`


TODO
----

* Field weights
* All field types
* Runtime migrations
* ...