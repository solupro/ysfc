import os
import django.core.handlers.wsgi

import sys 
app_root = os.path.dirname(__file__) 
sys.path.insert(0,os.path.join(app_root,'djclub'))
sys.path.insert(0, os.path.join(app_root, 'virtualenv.bundle'))

import sae

os.environ['DJANGO_SETTINGS_MODULE'] = 'djclub.settings'

application = sae.create_wsgi_app(django.core.handlers.wsgi.WSGIHandler())