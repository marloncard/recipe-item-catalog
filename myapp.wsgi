import json
import sys

sys.path.insert(0, "/var/www/catalog")

from views import app as application

FLASK_SECRET = json.loads(
    open('/var/www/catalog/flask_secret.json', 'r').read())['flask_secret']

application.secret_key = FLASK_SECRET
