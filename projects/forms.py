from django import forms
from django.core.exceptions import ValidationError
from .models import Project, Task, ProjectStatus, ProjectPriority, TaskStatus
from django.utils.translation import gettext_lazy as _

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'status', 'priority', 
                 'start_date', 'due_date', 'is_repeatable']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        help_texts = {
            'is_repeatable': _('Marca esta opción si el proyecto puede reiniciarse'),
            'priority': _('Establece la prioridad para ordenar los proyectos'),
            'start_date': _('Fecha de inicio del proyecto (opcional)'),
            'due_date': _('Fecha límite del proyecto (opcional)'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ordenar estados y prioridades por orden
        self.fields['status'].queryset = ProjectStatus.objects.all().order_by('order')
        self.fields['priority'].queryset = ProjectPriority.objects.all().order_by('order')
        
        # Si es un nuevo proyecto, establecer el estado inicial
        if not self.instance.pk:
            initial_status = ProjectStatus.objects.filter(order=0).first()
            if initial_status:
                self.fields['status'].initial = initial_status

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        due_date = cleaned_data.get('due_date')

        if start_date and due_date:
            if start_date > due_date:
                raise ValidationError({
                    '__all__': _('La fecha de inicio no puede ser posterior a la fecha de vencimiento')
                })
        return cleaned_data

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['description', 'status', 'due_date', 'order']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }
        
    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project')
        super().__init__(*args, **kwargs)
        
        # Establecer el estado inicial por defecto para nuevas tareas
        if not self.instance.pk:
            initial_status = TaskStatus.objects.filter(order=0).first()
            if initial_status:
                self.initial['status'] = initial_status

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date and self.project.due_date and due_date > self.project.due_date:
            raise ValidationError(
                _('La fecha de vencimiento no puede ser posterior a la del proyecto')
            )
        return due_date

    def clean(self):
        cleaned_data = super().clean()
        if self.project:
            self.instance.project = self.project
        return cleaned_data

class ProjectStatusForm(forms.ModelForm):
    class Meta:
        model = ProjectStatus
        fields = ['name', 'description', 'order', 'is_final']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'order': _('Orden de visualización en el tablero (0 = primero)'),
            'is_final': _('Marca esta opción si este estado indica que el proyecto ha finalizado'),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if ProjectStatus.objects.filter(name__iexact=name).exclude(pk=self.instance.pk).exists():
            raise ValidationError(_('Ya existe un estado con este nombre'))
        return name

class ProjectPriorityForm(forms.ModelForm):
    class Meta:
        model = ProjectPriority
        fields = ['name', 'description', 'order', 'color']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'order': _('Orden de visualización (0 = primero)'),
            'color': _('Clase CSS de Bootstrap para el color (success, warning, danger, etc)'),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if ProjectPriority.objects.filter(name__iexact=name).exclude(pk=self.instance.pk).exists():
            raise ValidationError(_('Ya existe una prioridad con este nombre'))
        return name

class TaskStatusForm(forms.ModelForm):
    class Meta:
        model = TaskStatus
        fields = ['name', 'description', 'order', 'is_final']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'order': _('Orden de visualización (0 = primero)'),
            'is_final': _('Marca esta opción si este estado indica que la tarea ha finalizado'),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if TaskStatus.objects.filter(name__iexact=name).exclude(pk=self.instance.pk).exists():
            raise ValidationError(_('Ya existe un estado con este nombre'))
        return name