from datetime import date, timedelta


def kanban_columns():
    return ['Backlog', 'In lavorazione', 'In test', 'Completato']


def kanban_cards():
    return [
        {'id': 'T-100', 'title': 'Analisi requisiti', 'status': 'Backlog'},
        {'id': 'T-101', 'title': 'Setup ambiente', 'status': 'In lavorazione'},
        {'id': 'T-102', 'title': 'UI Kanban', 'status': 'In test'},
        {'id': 'T-103', 'title': 'Workflow engine', 'status': 'Backlog'},
    ]


def planner_items():
    start = date.today()
    return [
        {'id': 'P-10', 'title': 'Form login', 'due_date': start + timedelta(days=1)},
        {'id': 'P-11', 'title': 'Drag & drop', 'due_date': start + timedelta(days=3)},
        {'id': 'P-12', 'title': 'Integrazione VisionFlow', 'due_date': start + timedelta(days=5)},
    ]


def workflow_instances():
    return [
        {'id': 'WF-7', 'name': 'Onboarding', 'step': 'Verifica documenti'},
        {'id': 'WF-8', 'name': 'Richiesta accessi', 'step': 'Approvazione manager'},
        {'id': 'WF-9', 'name': 'Deploy release', 'step': 'QA'},
    ]
