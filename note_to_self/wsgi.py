import os

from django.core.wsgi import get_wsgi_application
from dj_static import Cling
from dotenv import load_dotenv

load_dotenv('.env')
DJANGO_SETTINGS_MODULE = os.getenv("DJANGO_SETTINGS_MODULE")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', DJANGO_SETTINGS_MODULE)
application = Cling(get_wsgi_application())
