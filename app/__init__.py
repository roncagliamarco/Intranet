"""Application factory for the intranet portal."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from flask import Flask
from flask_login import LoginManager

from .config import Config, load_env_config
from .ldap_auth import LdapAuthenticator

login_manager = LoginManager()


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    """Create and configure a Flask application.

    Args:
        test_config: Optional dictionary to override configuration for testing.

    Returns:
        Configured Flask application instance.
    """

    config_source = test_config or load_env_config()
    config = Config.from_flask(config_source)
    app = Flask(__name__)
    app.config.update(config.model_dump())

    _configure_logging(app)
    _configure_authentication(app, config)

    from .routes import bp as main_bp

    app.register_blueprint(main_bp)

    @app.route("/health")
    def health() -> str:  # pragma: no cover - trivial
        return "ok"

    return app


def _configure_logging(app: Flask) -> None:
    log_level = app.config.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=getattr(logging, log_level, logging.INFO))


def _configure_authentication(app: Flask, config: Config) -> None:
    login_manager.init_app(app)
    login_manager.login_view = "main.login"

    authenticator = LdapAuthenticator(config)

    @login_manager.user_loader
    def load_user(username: str):  # pragma: no cover - flask-login callback
        return authenticator.get_user(username)

    app.extensions["ldap_authenticator"] = authenticator


def get_instance_path() -> Path:
    """Return the instance path used by Flask."""

    return Path(__file__).resolve().parent.parent / "instance"
