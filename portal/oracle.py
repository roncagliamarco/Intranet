from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from django.conf import settings

try:
    import cx_Oracle
except Exception:  # pragma: no cover - optional
    cx_Oracle = None


def _connect():
    cfg = settings.ORACLE_CONFIG
    if not (cx_Oracle and cfg.get('DSN')):
        return None
    return cx_Oracle.connect(cfg['USERNAME'], cfg['PASSWORD'], cfg['DSN'])


def fetch_menu() -> List['MenuEntry']:
    conn = _connect()
    if conn:
        cur = conn.cursor()
        cur.execute('SELECT label, path, parent_label FROM INTRANET_MENU ORDER BY sort_order')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        entries = [MenuEntry(label=r[0], path=r[1], parent=r[2]) for r in rows]
    else:
        entries = [
            MenuEntry('Dashboard', '#dashboard'),
            MenuEntry('Kanban', '#kanban'),
            MenuEntry('Planner', '#planner'),
            MenuEntry('Workflow', '#workflow'),
            MenuEntry('Amministrazione', None, children=[
                MenuEntry('Utenti', '#admin/users'),
                MenuEntry('Ruoli', '#admin/roles'),
            ]),
        ]
    return _nest_menu(entries)


def update_kanban(card_id: str, new_status: str) -> bool:
    conn = _connect()
    if conn:
        cur = conn.cursor()
        cur.execute('UPDATE INTRANET_TASK SET status = :status WHERE id = :id', {'status': new_status, 'id': card_id})
        conn.commit()
        cur.close()
        conn.close()
    return True


def shift_planner(task_id: str, delta_days: int) -> bool:
    conn = _connect()
    if conn:
        cur = conn.cursor()
        cur.execute('UPDATE INTRANET_PLANNER SET due_date = due_date + :delta WHERE id = :id', {'delta': delta_days, 'id': task_id})
        conn.commit()
        cur.close()
        conn.close()
    return True


def advance_workflow(instance_id: str, step: str) -> bool:
    conn = _connect()
    if conn:
        cur = conn.cursor()
        cur.execute('UPDATE INTRANET_WORKFLOW SET current_step = :step WHERE id = :id', {'step': step, 'id': instance_id})
        conn.commit()
        cur.close()
        conn.close()
    return True


@dataclass
class MenuEntry:
    label: str
    path: Optional[str] = None
    parent: Optional[str] = None
    children: Optional[List['MenuEntry']] = None


def _nest_menu(entries: List['MenuEntry']) -> List['MenuEntry']:
    by_label = {e.label: e for e in entries}
    roots: List[MenuEntry] = []
    for entry in entries:
        entry.children = entry.children or []
    for entry in entries:
        if entry.parent and entry.parent in by_label:
            by_label[entry.parent].children.append(entry)
        else:
            roots.append(entry)
    return roots
