"""Planner-style timeline helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List

import cx_Oracle

from .config import Config


@dataclass
class PlannerItem:
    id: int
    title: str
    start: date
    end: date
    owner: str


class PlannerService:
    def __init__(self, config: Config):
        self.config = config

    def load_items(self) -> list[PlannerItem]:
        if not self.config.oracle_dsn:
            return self._demo_items()
        return self._fetch_items_from_oracle()

    def shift_item(self, item_id: int, days: int) -> None:
        if not self.config.oracle_dsn:
            return
        with cx_Oracle.connect(
            user=self.config.oracle_username,
            password=self.config.oracle_password,
            dsn=self.config.oracle_dsn,
        ) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE INTRANET_PLANNER
                SET START_DATE = START_DATE + :days,
                    END_DATE = END_DATE + :days
                WHERE ID = :item_id
                """,
                days=days,
                item_id=item_id,
            )
            conn.commit()

    def _fetch_items_from_oracle(self) -> list[PlannerItem]:  # pragma: no cover - requires DB
        with cx_Oracle.connect(
            user=self.config.oracle_username,
            password=self.config.oracle_password,
            dsn=self.config.oracle_dsn,
        ) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT ID, TITLE, START_DATE, END_DATE, OWNER
                FROM INTRANET_PLANNER
                ORDER BY START_DATE
                """
            )
            return [PlannerItem(*row) for row in cursor.fetchall()]

    def _demo_items(self) -> list[PlannerItem]:
        return [
            PlannerItem(id=1, title="Analisi", start=date(2024, 8, 1), end=date(2024, 8, 5), owner="Luca"),
            PlannerItem(id=2, title="Sviluppo", start=date(2024, 8, 6), end=date(2024, 8, 15), owner="Sara"),
            PlannerItem(id=3, title="Collaudo", start=date(2024, 8, 16), end=date(2024, 8, 20), owner="Marco"),
        ]
