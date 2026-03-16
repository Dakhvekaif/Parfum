import os
import sys

# 1. Virtualenv
venv = '/home/au7nyctaofmw/virtualenv/Parfum-Backend/Parfum/backend/3.11/lib/python3.11/site-packages'
if venv not in sys.path:
    sys.path.insert(0, venv)

# 2. Project Root (where manage.py is)
root = '/home/au7nyctaofmw/Parfum-Backend/Parfum/backend'
if root not in sys.path:
    sys.path.insert(0, root)

# 3. Set the settings to PARFUM
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parfum.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()