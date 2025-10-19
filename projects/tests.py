from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Project, Task, ProjectStatus, ProjectPriority, TaskStatus
from .forms import ProjectForm, TaskForm
from django.core.exceptions import ValidationError

class ProjectModelTest(TestCase):
    def setUp(self):
        # Obtener estados y prioridades existentes
        self.status_todo = ProjectStatus.objects.get(slug='todo')
        self.status_completed = ProjectStatus.objects.get(slug='completed')
        self.priority_medium = ProjectPriority.objects.get(slug='medium')
        self.task_status_todo = TaskStatus.objects.get(slug='todo')
        self.task_status_completed = TaskStatus.objects.get(slug='completed')
        
        self.project = Project.objects.create(
            title="Proyecto de Prueba",
            description="Descripción del proyecto de prueba",
            status=self.status_todo,
            priority=self.priority_medium,
            start_date=timezone.now().date(),
            due_date=(timezone.now() + timedelta(days=7)).date(),
            is_repeatable=True
        )
        
        self.task = Task.objects.create(
            project=self.project,
            description="Tarea de prueba",
            status=self.task_status_todo,
            order=0
        )

    def test_project_creation(self):
        self.assertTrue(isinstance(self.project, Project))
        self.assertEqual(str(self.project), "Proyecto de Prueba")

    def test_task_creation(self):
        self.assertTrue(isinstance(self.task, Task))
        self.assertTrue(str(self.task).startswith("Proyecto de Prueba -"))

    def test_completion_percentage(self):
        # Inicialmente 0% completado porque ninguna tarea está en estado final
        self.assertEqual(self.project.completion_percentage(), 0)

        # Crear una tarea en estado final
        Task.objects.create(
            project=self.project,
            description="Tarea completada",
            status=self.task_status_completed,
            order=1
        )

        # Debe ser 50% completado (1 de 2 tareas)
        self.assertEqual(self.project.completion_percentage(), 50)

    def test_task_ordering(self):
        """Prueba que las tareas se ordenen correctamente por el campo order"""
        # Crear más tareas con diferentes órdenes
        Task.objects.create(
            project=self.project,
            description="Tarea 3",
            status=self.task_status_todo,
            order=3
        )
        Task.objects.create(
            project=self.project,
            description="Tarea 1",
            status=self.task_status_todo,
            order=1
        )
        
        tasks = self.project.tasks.all()
        self.assertEqual(tasks[0].order, 0)  # La tarea original
        self.assertEqual(tasks[1].order, 1)
        self.assertEqual(tasks[2].order, 3)

    def test_project_with_dates(self):
        """Prueba la validación de fechas del proyecto"""
        project = Project(
            title="Proyecto con Fechas",
            status=self.status_todo,
            priority=self.priority_medium,
            start_date=timezone.now().date() + timedelta(days=5),
            due_date=timezone.now().date()
        )
        
        with self.assertRaises(ValidationError):
            project.full_clean()

    def test_task_with_dates(self):
        """Prueba la validación de fechas de las tareas"""
        # Establecer una fecha de vencimiento para el proyecto
        self.project.due_date = timezone.now().date() + timedelta(days=10)
        self.project.save()

        # Intentar crear una tarea con fecha posterior
        task = Task(
            project=self.project,
            description="Tarea con fecha inválida",
            status=self.task_status_todo,
            due_date=self.project.due_date + timedelta(days=1)
        )
        
        with self.assertRaises(ValidationError):
            task.full_clean()

class ProjectFormTest(TestCase):
    def setUp(self):
        # Obtener estados y prioridades existentes
        self.status_todo = ProjectStatus.objects.get(slug='todo')
        self.priority_medium = ProjectPriority.objects.get(slug='medium')

    def test_valid_project_form(self):
        form_data = {
            'title': 'Nuevo Proyecto',
            'description': 'Descripción del nuevo proyecto',
            'status': self.status_todo.id,
            'priority': self.priority_medium.id,
            'start_date': timezone.now().date(),
            'due_date': (timezone.now() + timedelta(days=7)).date(),
            'is_repeatable': False
        }
        form = ProjectForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_project_form(self):
        # Formulario sin título (campo requerido)
        form_data = {
            'description': 'Descripción del nuevo proyecto',
            'status': self.status_todo.id,
            'priority': self.priority_medium.id
        }
        form = ProjectForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_project_dates_validation(self):
        """Prueba validaciones adicionales de fechas en el formulario"""
        # Fecha de inicio en el futuro y fecha de vencimiento en el pasado
        past_date = timezone.now().date() - timedelta(days=5)
        future_date = timezone.now().date() + timedelta(days=5)
        
        form_data = {
            'title': 'Proyecto con Fechas',
            'status': self.status_todo.id,
            'priority': self.priority_medium.id,
            'start_date': future_date,
            'due_date': past_date
        }
        form = ProjectForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('La fecha de inicio no puede ser posterior a la fecha de vencimiento', 
                     str(form.errors))

class TaskFormTest(TestCase):
    def setUp(self):
        # Obtener estados y prioridades existentes
        self.status_todo = ProjectStatus.objects.get(slug='todo')
        self.priority_medium = ProjectPriority.objects.get(slug='medium')
        
        self.project = Project.objects.create(
            title="Proyecto para Tareas",
            status=self.status_todo,
            priority=self.priority_medium,
            due_date=(timezone.now() + timedelta(days=7)).date()
        )

    def test_valid_task_form(self):
        form_data = {
            'description': 'Nueva Tarea',
            'status': Task.Status.TODO,
            'order': 0
        }
        form = TaskForm(data=form_data, project=self.project)
        self.assertTrue(form.is_valid())

    def test_invalid_task_form(self):
        # Formulario sin descripción (campo requerido)
        form_data = {
            'status': Task.Status.TODO,
            'order': 0
        }
        form = TaskForm(data=form_data, project=self.project)
        self.assertFalse(form.is_valid())
        self.assertIn('description', form.errors)

    def test_task_due_date_validation(self):
        """Prueba que la fecha de vencimiento de la tarea no sea posterior a la del proyecto"""
        self.project.due_date = timezone.now().date() + timedelta(days=5)
        self.project.save()

        form_data = {
            'description': 'Tarea con fecha posterior',
            'status': Task.Status.TODO,
            'due_date': self.project.due_date + timedelta(days=1),
            'order': 0
        }
        form = TaskForm(data=form_data, project=self.project)
        self.assertFalse(form.is_valid())
        self.assertIn('due_date', form.errors)

class ProjectViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Obtener estados y prioridades existentes
        self.status_todo = ProjectStatus.objects.get(slug='todo')
        self.status_completed = ProjectStatus.objects.get(slug='completed')
        self.priority_medium = ProjectPriority.objects.get(slug='medium')
        self.task_status_todo = TaskStatus.objects.get(slug='todo')
        self.task_status_completed = TaskStatus.objects.get(slug='completed')
        
        self.project = Project.objects.create(
            title="Proyecto de Prueba",
            status=self.status_todo,
            priority=self.priority_medium
        )

    def test_kanban_board_view(self):
        response = self.client.get(reverse('projects:kanban-board'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/kanban_board.html')
        self.assertContains(response, "Proyecto de Prueba")

    def test_project_detail_view(self):
        response = self.client.get(
            reverse('projects:project-detail', kwargs={'pk': self.project.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/project_detail.html')
        self.assertContains(response, self.project.title)

    def test_project_create_view(self):
        response = self.client.get(reverse('projects:project-create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/project_form.html')

        # Probar la creación de un proyecto
        project_data = {
            'title': 'Nuevo Proyecto Test',
            'description': 'Descripción del proyecto test',
            'status': self.status_todo.id,
            'priority': self.priority_medium.id,
        }
        response = self.client.post(reverse('projects:project-create'), project_data)
        self.assertEqual(response.status_code, 302)  # Redirección después de crear
        self.assertTrue(Project.objects.filter(title='Nuevo Proyecto Test').exists())

    def test_project_update_view(self):
        response = self.client.get(
            reverse('projects:project-update', kwargs={'pk': self.project.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/project_form.html')

        # Probar la actualización del proyecto
        updated_data = {
            'title': 'Proyecto Actualizado',
            'description': 'Nueva descripción',
            'status': self.status_completed.id,
            'priority': self.priority_medium.id,
        }
        response = self.client.post(
            reverse('projects:project-update', kwargs={'pk': self.project.pk}),
            updated_data
        )
        self.assertEqual(response.status_code, 302)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, 'Proyecto Actualizado')

    def test_project_delete_view(self):
        response = self.client.post(
            reverse('projects:project-delete', kwargs={'pk': self.project.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())

    def test_unauthorized_access(self):
        self.client.logout()
        response = self.client.get(reverse('projects:kanban-board'))
        self.assertEqual(response.status_code, 302)  # Redirección al login
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_project_restart(self):
        """Prueba la funcionalidad de reinicio de proyectos"""
        # Crear un proyecto repetible con tareas
        project = Project.objects.create(
            title="Proyecto Repetible",
            status=self.status_todo,
            priority=self.priority_medium,
            is_repeatable=True
        )

        # Crear algunas tareas en diferentes estados
        Task.objects.create(
            project=project,
            description="Tarea 1",
            status=self.task_status_completed,
            order=0
        )
        Task.objects.create(
            project=project,
            description="Tarea 2",
            status=self.task_status_completed,
            order=1
        )

        # Intentar reiniciar el proyecto
        response = self.client.post(reverse('projects:project-restart', kwargs={'pk': project.pk}))
        self.assertEqual(response.status_code, 302)

        # Verificar que todas las tareas estén en estado TODO
        project.refresh_from_db()
        for task in project.tasks.all():
            self.assertEqual(task.status, self.task_status_todo)

    def test_project_restart_non_repeatable(self):
        """Prueba que no se pueda reiniciar un proyecto no repetible"""
        project = Project.objects.create(
            title="Proyecto No Repetible",
            status=self.status_completed,
            priority=self.priority_medium,
            is_repeatable=False
        )

        response = self.client.post(reverse('projects:project-restart', kwargs={'pk': project.pk}))
        self.assertEqual(response.status_code, 302)
        
        # Verificar que se muestre un mensaje de error
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any('no es repetible' in str(message) for message in messages))

    def test_project_filtering(self):
        """Prueba el filtrado de proyectos por estado"""
        # Crear proyectos en diferentes estados
        Project.objects.create(
            title="Proyecto En Progreso",
            status=self.status_todo,
            priority=self.priority_medium
        )
        Project.objects.create(
            title="Proyecto Completado",
            status=self.status_completed,
            priority=self.priority_medium
        )

        response = self.client.get(reverse('projects:kanban-board'))
        self.assertEqual(response.status_code, 200)
        
        # Verificar que los proyectos estén organizados por estado
        context = response.context
        self.assertTrue('status_projects' in context)

    def test_task_ordering_in_view(self):
        """Prueba que las tareas se muestren ordenadas en la vista de detalle"""
        # Crear tareas con diferentes órdenes
        Task.objects.create(
            project=self.project,
            description="Última Tarea",
            status=self.task_status_todo,
            order=2
        )
        Task.objects.create(
            project=self.project,
            description="Primera Tarea",
            status=self.task_status_todo,
            order=0
        )

        response = self.client.get(
            reverse('projects:project-detail', kwargs={'pk': self.project.pk})
        )
        self.assertEqual(response.status_code, 200)
        
        tasks = response.context['tasks']
        self.assertEqual(tasks[0].order, 0)
        self.assertEqual(tasks[1].order, 2)

class TaskViewsTest(TestCase):
    """Nueva clase de pruebas específica para las vistas de tareas"""
    def setUp(self):
        self.client = Client()
        
        # Obtener estados y prioridades existentes
        self.status_todo = ProjectStatus.objects.get(slug='todo')
        self.priority_medium = ProjectPriority.objects.get(slug='medium')
        self.task_status_todo = TaskStatus.objects.get(slug='todo')
        self.task_status_completed = TaskStatus.objects.get(slug='completed')
        
        self.project = Project.objects.create(
            title="Proyecto para Tareas",
            status=self.status_todo,
            priority=self.priority_medium
        )
        self.task = Task.objects.create(
            project=self.project,
            description="Tarea de Prueba",
            status=self.task_status_todo,
            order=0
        )

    def test_task_create_view(self):
        """Prueba la creación de tareas"""
        response = self.client.get(
            reverse('projects:task-create', kwargs={'project_id': self.project.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/task_form.html')

        # Probar la creación de una tarea
        task_data = {
            'description': 'Nueva Tarea Test',
            'status': self.task_status_todo.id,
            'order': 1
        }
        response = self.client.post(
            reverse('projects:task-create', kwargs={'project_id': self.project.pk}),
            task_data
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Task.objects.filter(description='Nueva Tarea Test', project=self.project).exists()
        )

    def test_task_update_view(self):
        """Prueba la actualización de tareas"""
        response = self.client.get(
            reverse('projects:task-update', kwargs={'pk': self.task.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/task_form.html')

        # Probar la actualización de la tarea
        updated_data = {
            'description': 'Tarea Actualizada',
            'status': self.task_status_completed.id,
            'order': 2
        }
        response = self.client.post(
            reverse('projects:task-update', kwargs={'pk': self.task.pk}),
            updated_data
        )
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.description, 'Tarea Actualizada')
        self.assertEqual(self.task.status, self.task_status_completed)

    def test_task_delete_view(self):
        """Prueba la eliminación de tareas"""
        response = self.client.post(
            reverse('projects:task-delete', kwargs={'pk': self.task.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())
