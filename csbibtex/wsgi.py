"""
WSGI config for csbibtex project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "csbibtex.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


"""
From: http://projects.unbit.it/uwsgi/wiki/TipsAndTricks#uWSGIdjangoautoreloadmode
"""
"""
import uwsgi
from uwsgidecorators import timer
from django.utils import autoreload

@timer(3)
def change_code_gracefull_reload(sig):
    if autoreload.code_changed():
        uwsgi.reload()
"""
