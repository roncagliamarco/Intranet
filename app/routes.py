"""Flask routes for the intranet demo."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from flask import Blueprint, current_app, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user

from .config import Config
from .kanban import KanbanService
from .menu_service import MenuService
from .planner import PlannerService
from .workflow import WorkflowService

bp = Blueprint("main", __name__)


def _services():
    config = Config.from_flask(current_app.config)
    return {
        "menu": MenuService(config),
        "kanban": KanbanService(config),
        "planner": PlannerService(config),
        "workflow": WorkflowService(config),
    }


@bp.route("/")
@login_required
def index():
    services = _services()
    return render_template(
        "index.html",
        menu=services["menu"].load_menu(),
        kanban_columns=services["kanban"].load_board(),
        planner_items=services["planner"].load_items(),
        workflow_steps=services["workflow"].load_steps(),
    )


@bp.route("/login", methods=["GET", "POST"])
def login():
    authenticator = current_app.extensions["ldap_authenticator"]
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        user = authenticator.authenticate(username, password)
        if user:
            login_user(user)
            return redirect(url_for("main.index"))
        return render_template("login.html", error="Credenziali non valide")
    return render_template("login.html")


@bp.route("/logout")
@login_required
def logout():  # pragma: no cover - trivial
    logout_user()
    return redirect(url_for("main.login"))


@bp.route("/api/kanban/move", methods=["POST"])
@login_required
def api_move_task():
    payload: dict[str, Any] = request.get_json(force=True)
    task_id = int(payload["taskId"])
    status = payload["status"]
    services = _services()
    services["kanban"].move_task(task_id, status)
    return ("", 204)


@bp.route("/api/planner/shift", methods=["POST"])
@login_required
def api_shift_item():
    payload: dict[str, Any] = request.get_json(force=True)
    services = _services()
    services["planner"].shift_item(int(payload["itemId"]), int(payload["days"]))
    return ("", 204)


@bp.route("/api/workflow/advance", methods=["POST"])
@login_required
def api_advance_workflow():
    payload: dict[str, Any] = request.get_json(force=True)
    services = _services()
    services["workflow"].advance_step(int(payload["stepId"]), payload["status"])
    return ("", 204)


@bp.app_template_filter("date")
def format_date(value: datetime, fmt: str = "%d/%m"):
    return value.strftime(fmt) if value else ""
