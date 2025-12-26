"""Workflow integration stub (VisionFlow-like)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import cx_Oracle

from .config import Config


@dataclass
class WorkflowStep:
    id: int
    name: str
    status: str
    assigned_to: str | None = None


class WorkflowService:
    def __init__(self, config: Config):
        self.config = config

    def load_steps(self) -> list[WorkflowStep]:
        if not self.config.oracle_dsn:
            return self._demo_steps()
        return self._fetch_steps_from_oracle()

    def advance_step(self, step_id: int, status: str) -> None:
        if not self.config.oracle_dsn:
            return
        with cx_Oracle.connect(
            user=self.config.oracle_username,
            password=self.config.oracle_password,
            dsn=self.config.oracle_dsn,
        ) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE INTRANET_WORKFLOW SET STATUS = :status WHERE ID = :step_id",
                status=status,
                step_id=step_id,
            )
            conn.commit()

    def _fetch_steps_from_oracle(self) -> list[WorkflowStep]:  # pragma: no cover - requires DB
        with cx_Oracle.connect(
            user=self.config.oracle_username,
            password=self.config.oracle_password,
            dsn=self.config.oracle_dsn,
        ) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT ID, NAME, STATUS, ASSIGNED_TO
                FROM INTRANET_WORKFLOW
                ORDER BY ID
                """
            )
            return [WorkflowStep(*row) for row in cursor.fetchall()]

    def _demo_steps(self) -> list[WorkflowStep]:
        return [
            WorkflowStep(id=1, name="Inizio", status="aperto", assigned_to="PM"),
            WorkflowStep(id=2, name="Analisi", status="in_corso", assigned_to="Analyst"),
            WorkflowStep(id=3, name="Approvazione", status="in_attesa", assigned_to="Stakeholder"),
        ]
