import sys

sys.path.insert(0, "/var/www/catalog")

from views import app as application

application.secret_key='585jOph9'
