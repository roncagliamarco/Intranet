import json
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from . import demo
from .forms import LoginForm
from .oracle import advance_workflow, fetch_menu, shift_planner, update_kanban


def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        if user:
            login(request, user)
            messages.success(request, 'Accesso effettuato con successo.')
            return redirect('dashboard')
        messages.error(request, 'Credenziali non valide o LDAP non disponibile.')

    return render(request, 'login.html', {'form': form, 'settings': settings})


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect('login')


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    menu = fetch_menu()
    context = {
        'menu': menu,
        'kanban_columns': demo.kanban_columns(),
        'kanban_cards': demo.kanban_cards(),
        'planner_items': demo.planner_items(),
        'workflow_instances': demo.workflow_instances(),
    }
    return render(request, 'dashboard.html', context)


@require_POST
@login_required
def api_kanban_move(request: HttpRequest) -> JsonResponse:
    try:
        payload = json.loads(request.body.decode())
        update_kanban(payload['cardId'], payload['newStatus'])
        return JsonResponse({'ok': True})
    except Exception as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=400)


@require_POST
@login_required
def api_planner_shift(request: HttpRequest) -> JsonResponse:
    try:
        payload = json.loads(request.body.decode())
        delta = int(payload['delta'])
        shift_planner(payload['taskId'], delta)
        return JsonResponse({'ok': True, 'shiftedTo': (datetime.utcnow().date()).isoformat()})
    except Exception as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=400)


@require_POST
@login_required
def api_workflow_advance(request: HttpRequest) -> JsonResponse:
    try:
        payload = json.loads(request.body.decode())
        advance_workflow(payload['instanceId'], payload['step'])
        return JsonResponse({'ok': True})
    except Exception as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=400)
