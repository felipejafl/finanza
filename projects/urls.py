from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.KanbanBoardView.as_view(), name='kanban-board'),
    path('project/new/', views.ProjectCreateView.as_view(), name='project-create'),
    path('project/<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('project/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project-update'),
    path('project/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project-delete'),
    path('project/<int:pk>/restart/', views.restart_project, name='project-restart'),
    path('project/<int:project_id>/task/new/', views.TaskCreateView.as_view(), name='task-create'),
    path('task/<int:pk>/edit/', views.TaskUpdateView.as_view(), name='task-update'),
    path('task/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task-delete'),
    path('status/new/', views.ProjectStatusCreateView.as_view(), name='status-create'),
    path('priority/new/', views.ProjectPriorityCreateView.as_view(), name='priority-create'),
]