const kanbanTasks = document.querySelectorAll('.kanban-card');
const kanbanColumns = document.querySelectorAll('.kanban-tasks');

kanbanTasks.forEach(card => {
  card.addEventListener('dragstart', () => card.classList.add('dragging'));
  card.addEventListener('dragend', event => {
    card.classList.remove('dragging');
    const column = card.closest('.kanban-tasks');
    const status = column.dataset.status;
    fetch('/api/kanban/move', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ taskId: card.dataset.id, status })
    });
  });
});

kanbanColumns.forEach(column => {
  column.addEventListener('dragover', event => {
    event.preventDefault();
    const dragging = document.querySelector('.kanban-card.dragging');
    if (dragging && !column.contains(dragging)) {
      column.appendChild(dragging);
    }
  });
});

// Planner
const plannerButtons = document.querySelectorAll('.planner-actions button');
plannerButtons.forEach(button => {
  button.addEventListener('click', () => {
    const shift = parseInt(button.dataset.shift, 10);
    const item = button.closest('.planner-item');
    fetch('/api/planner/shift', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ itemId: item.dataset.id, days: shift })
    });
  });
});

// Workflow
const workflowButtons = document.querySelectorAll('.workflow-actions button');
workflowButtons.forEach(button => {
  button.addEventListener('click', () => {
    const step = button.closest('.workflow-step');
    fetch('/api/workflow/advance', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ stepId: step.dataset.id, status: button.dataset.status })
    });
  });
});
