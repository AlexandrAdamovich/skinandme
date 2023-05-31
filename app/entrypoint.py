import logging

from flask import Flask

from app.api import api
from app.config import EnvironmentConfig
from app.extensions import db

from celery import Celery, Task
from app import celeryconfig


def create_app(env: str) -> Flask:
    """Application factory."""

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [sev %(levelno)s] [%(levelname)s] [%(name)s]> %(message)s",
        datefmt="%a, %d %b %Y %H:%M:%S",
    )

    app = Flask(__name__)

    conf = _load_configuration(env)
    app.config.from_object(conf)

    _register_extensions(app)

    with app.app_context():
        _register_blueprints(app)
        db.create_all()

    celery_init_app(app)

    return app


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.config_from_object(celeryconfig)
    celery_app.set_default()
    app.extensions["celery"] = celery_app

    return celery_app


def _load_configuration(env: str) -> str:
    """Load application configuration."""

    configurations = {
        EnvironmentConfig.TESTING.value: "app.config.TestingConfig",
        EnvironmentConfig.DEVELOPMENT.value: "app.config.Config",
    }

    conf = configurations.get(env)
    if not conf:
        raise RuntimeError(f"Could not load configuration {env=}")

    return conf


def _register_blueprints(app: Flask) -> None:
    """Register application blueprints."""

    app.register_blueprint(api)


def _register_extensions(app: Flask) -> None:
    """Register application extensions."""

    db.init_app(app)
