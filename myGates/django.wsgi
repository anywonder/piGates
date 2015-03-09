import os, sys
sys.path.append('/home/pi/Projects/Django')
sys.path.append('/home/pi/Projects/Django/myGates')

os.environ['DJANGO_SETTINGS_MODULE'] = 'myGates.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
