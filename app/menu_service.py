"""Menu retrieval and transformation logic."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

import cx_Oracle

from .config import Config


@dataclass
class MenuEntry:
    label: str
    url: str | None = None
    icon: str | None = None
    children: List["MenuEntry"] | None = None


class MenuService:
    """Load menu items from an Oracle table."""

    def __init__(self, config: Config):
        self.config = config

    def load_menu(self) -> list[MenuEntry]:
        if not self.config.oracle_dsn:
            return self._demo_menu()
        return list(self._fetch_menu_from_oracle())

    def _fetch_menu_from_oracle(self) -> Iterable[MenuEntry]:  # pragma: no cover - requires DB
        connection = cx_Oracle.connect(
            user=self.config.oracle_username,
            password=self.config.oracle_password,
            dsn=self.config.oracle_dsn,
        )
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT LABEL, URL, ICON, PARENT_LABEL
            FROM INTRANET_MENU
            ORDER BY PARENT_LABEL NULLS FIRST, LABEL
            """
        )
        rows = cursor.fetchall()
        connection.close()

        entries: dict[str, MenuEntry] = {}
        roots: list[MenuEntry] = []

        for label, url, icon, parent_label in rows:
            entry = MenuEntry(label=label, url=url, icon=icon, children=[])
            entries[label] = entry
            if parent_label:
                parent = entries.setdefault(parent_label, MenuEntry(label=parent_label, children=[]))
                parent.children = parent.children or []
                parent.children.append(entry)
            else:
                roots.append(entry)

        return roots

    def _demo_menu(self) -> list[MenuEntry]:
        return [
            MenuEntry(
                label="Dashboard",
                url="/",
                icon="grid",
            ),
            MenuEntry(
                label="Progetti",
                icon="folder",
                children=[
                    MenuEntry(label="Kanban", url="/kanban"),
                    MenuEntry(label="Planner", url="/planner"),
                ],
            ),
            MenuEntry(label="Workflow", url="/workflow", icon="repeat"),
        ]
