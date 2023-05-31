import os

from app.entrypoint import create_app

flask_app = create_app(os.environ.get("FLASK_ENV", "development"))
celery_app = flask_app.extensions["celery"]
