"""Kanban board domain model and helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import cx_Oracle

from .config import Config


@dataclass
class KanbanTask:
    id: int
    title: str
    status: str
    assignee: str | None = None
    description: str | None = None


@dataclass
class KanbanColumn:
    key: str
    title: str
    tasks: List[KanbanTask] = field(default_factory=list)


class KanbanService:
    def __init__(self, config: Config):
        self.config = config

    def load_board(self) -> list[KanbanColumn]:
        if not self.config.oracle_dsn:
            return self._demo_board()
        return self._fetch_board_from_oracle()

    def move_task(self, task_id: int, new_status: str) -> None:
        if not self.config.oracle_dsn:
            return
        with cx_Oracle.connect(
            user=self.config.oracle_username,
            password=self.config.oracle_password,
            dsn=self.config.oracle_dsn,
        ) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE INTRANET_TASK SET STATUS = :status WHERE ID = :task_id",
                status=new_status,
                task_id=task_id,
            )
            conn.commit()

    def _fetch_board_from_oracle(self) -> list[KanbanColumn]:  # pragma: no cover - requires DB
        with cx_Oracle.connect(
            user=self.config.oracle_username,
            password=self.config.oracle_password,
            dsn=self.config.oracle_dsn,
        ) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT ID, TITLE, STATUS, ASSIGNEE, DESCRIPTION
                FROM INTRANET_TASK
                """
            )
            rows = cursor.fetchall()

        columns: dict[str, KanbanColumn] = {}
        for row in rows:
            task = KanbanTask(*row)
            columns.setdefault(task.status, KanbanColumn(key=task.status, title=task.status)).tasks.append(task)

        return list(columns.values())

    def _demo_board(self) -> list[KanbanColumn]:
        todo = KanbanColumn(
            key="todo",
            title="Da fare",
            tasks=[
                KanbanTask(id=1, title="Analisi requisiti", status="todo", assignee="Luca"),
                KanbanTask(id=2, title="Setup ambiente", status="todo", assignee="Sara"),
            ],
        )
        doing = KanbanColumn(
            key="doing",
            title="In corso",
            tasks=[KanbanTask(id=3, title="LDAP integration", status="doing", assignee="Marco")],
        )
        done = KanbanColumn(
            key="done",
            title="Completato",
            tasks=[KanbanTask(id=4, title="Menu Oracle", status="done", assignee="Giulia")],
        )
        return [todo, doing, done]
