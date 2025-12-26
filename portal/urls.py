from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('api/kanban/move', views.api_kanban_move, name='api-kanban-move'),
    path('api/planner/shift', views.api_planner_shift, name='api-planner-shift'),
    path('api/workflow/advance', views.api_workflow_advance, name='api-workflow-advance'),
    path('', views.dashboard, name='dashboard'),
]
