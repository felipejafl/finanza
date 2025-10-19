from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Count
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Project, Task, ProjectStatus, ProjectPriority, TaskStatus
from .forms import ProjectForm, TaskForm, ProjectStatusForm, ProjectPriorityForm

class KanbanBoardView(ListView):
    model = Project
    template_name = 'projects/kanban_board.html'
    context_object_name = 'projects'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        projects = self.get_queryset()
        
        # Obtener todos los estados ordenados
        statuses = ProjectStatus.objects.order_by('order')
        
        # Organizar proyectos por estado
        status_projects = {
            status: projects.filter(status=status)
            for status in statuses
        }
        context['status_projects'] = status_projects
        return context

class ProjectDetailView(DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tasks = self.object.tasks.all()
        context['tasks'] = tasks
        context['completed_tasks_count'] = tasks.filter(status__is_final=True).count()
        return context

class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('projects:kanban-board')

    def form_valid(self, form):
        messages.success(self.request, _('Proyecto creado exitosamente'))
        return super().form_valid(form)

class ProjectUpdateView(UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    
    def get_success_url(self):
        messages.success(self.request, _('Proyecto actualizado exitosamente'))
        return reverse_lazy('projects:project-detail', kwargs={'pk': self.object.pk})

class ProjectDeleteView(DeleteView):
    model = Project
    template_name = 'projects/project_confirm_delete.html'
    success_url = reverse_lazy('projects:kanban-board')

    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Proyecto eliminado exitosamente'))
        return super().delete(request, *args, **kwargs)

class TaskCreateView(CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'projects/task_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = get_object_or_404(Project, pk=self.kwargs['project_id'])
        return kwargs

    def form_valid(self, form):
        form.instance.project = get_object_or_404(Project, id=self.kwargs['project_id'])
        messages.success(self.request, _('Tarea creada exitosamente'))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['project_id'])
        context['task_statuses'] = TaskStatus.objects.all().order_by('order')
        return context

    def get_success_url(self):
        return reverse_lazy('projects:project-detail', kwargs={'pk': self.kwargs['project_id']})

class TaskUpdateView(UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'projects/task_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.object.project
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.object.project
        context['task_statuses'] = TaskStatus.objects.all().order_by('order')
        return context

    def form_valid(self, form):
        messages.success(self.request, _('Tarea actualizada exitosamente'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('projects:project-detail', kwargs={'pk': self.object.project.pk})

class TaskDeleteView(DeleteView):
    model = Task
    template_name = 'projects/task_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Tarea eliminada exitosamente'))
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('projects:project-detail', kwargs={'pk': self.object.project.pk})

class ProjectStatusCreateView(CreateView):
    model = ProjectStatus
    form_class = ProjectStatusForm
    template_name = 'projects/status_form.html'
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('projects:kanban-board')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            context = {'status': self.object, 'form': ProjectForm()}
            html = render_to_string('projects/status_select_option.html', context, request=self.request)
            return JsonResponse({
                'status': 'success',
                'message': 'Estado creado correctamente',
                'html': html,
                'status_id': self.object.id
            })
        messages.success(self.request, 'Estado creado correctamente')
        return response

class ProjectPriorityCreateView(CreateView):
    model = ProjectPriority
    form_class = ProjectPriorityForm
    template_name = 'projects/priority_form.html'
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('projects:kanban-board')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            context = {'priority': self.object, 'form': ProjectForm()}
            html = render_to_string('projects/priority_select_option.html', context, request=self.request)
            return JsonResponse({
                'status': 'success',
                'message': 'Prioridad creada correctamente',
                'html': html,
                'priority_id': self.object.id
            })
        messages.success(self.request, 'Prioridad creada correctamente')
        return response

def restart_project(request, pk):
    """Vista para reiniciar un proyecto repetible"""
    project = get_object_or_404(Project, pk=pk)
    
    try:
        project.restart()
        messages.success(request, _('Proyecto reiniciado exitosamente'))
    except ValidationError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, _('Error al reiniciar el proyecto: {}').format(str(e)))
    
    return redirect('projects:project-detail', pk=pk)
