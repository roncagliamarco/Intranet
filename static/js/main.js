function getCsrfToken() {
  return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

function wireKanban() {
  document.querySelectorAll('.kanban-card').forEach(card => {
    card.addEventListener('dragstart', ev => {
      ev.dataTransfer.setData('text/plain', card.dataset.cardId);
    });
  });
  document.querySelectorAll('.kanban-column').forEach(col => {
    col.addEventListener('dragover', ev => ev.preventDefault());
    col.addEventListener('drop', ev => {
      ev.preventDefault();
      const cardId = ev.dataTransfer.getData('text/plain');
      const newStatus = col.dataset.status;
      const card = document.querySelector(`[data-card-id="${cardId}"]`);
      col.querySelector('.kanban-cards').appendChild(card);
      fetch('/api/kanban/move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        body: JSON.stringify({ cardId, newStatus })
      });
    });
  });
}

function wirePlanner() {
  document.querySelectorAll('.planner-item .shift').forEach(btn => {
    btn.addEventListener('click', () => {
      const taskId = btn.closest('.planner-item').dataset.taskId;
      const delta = btn.dataset.delta;
      fetch('/api/planner/shift', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        body: JSON.stringify({ taskId, delta })
      });
    });
  });
}

function wireWorkflow() {
  document.querySelectorAll('.workflow-item .advance').forEach(btn => {
    btn.addEventListener('click', () => {
      const item = btn.closest('.workflow-item');
      const instanceId = item.dataset.instanceId;
      const step = item.querySelector('.next-step').value || 'Avanzato';
      fetch('/api/workflow/advance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        body: JSON.stringify({ instanceId, step })
      });
    });
  });
}

document.addEventListener('DOMContentLoaded', () => {
  if (document.querySelector('.kanban-grid')) wireKanban();
  if (document.querySelector('#planner')) wirePlanner();
  if (document.querySelector('#workflow')) wireWorkflow();
});
