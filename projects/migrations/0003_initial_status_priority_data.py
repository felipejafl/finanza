from django.db import migrations

def create_initial_data(apps, schema_editor):
    ProjectStatus = apps.get_model('projects', 'ProjectStatus')
    ProjectPriority = apps.get_model('projects', 'ProjectPriority')

    # Crear estados iniciales
    statuses = [
        {'name': 'Idea', 'slug': 'idea', 'order': 0, 'is_final': False},
        {'name': 'Por Hacer', 'slug': 'todo', 'order': 1, 'is_final': False},
        {'name': 'En Progreso', 'slug': 'in-progress', 'order': 2, 'is_final': False},
        {'name': 'Completado', 'slug': 'completed', 'order': 3, 'is_final': True},
        {'name': 'Cancelado', 'slug': 'cancelled', 'order': 4, 'is_final': True},
    ]
    for status_data in statuses:
        ProjectStatus.objects.create(**status_data)

    # Crear prioridades iniciales
    priorities = [
        {'name': 'Baja', 'slug': 'low', 'order': 0, 'color': 'success'},
        {'name': 'Media', 'slug': 'medium', 'order': 1, 'color': 'warning'},
        {'name': 'Alta', 'slug': 'high', 'order': 2, 'color': 'danger'},
    ]
    for priority_data in priorities:
        ProjectPriority.objects.create(**priority_data)

def remove_initial_data(apps, schema_editor):
    ProjectStatus = apps.get_model('projects', 'ProjectStatus')
    ProjectPriority = apps.get_model('projects', 'ProjectPriority')
    ProjectStatus.objects.all().delete()
    ProjectPriority.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('projects', '0002_projectpriority_projectstatus_alter_project_priority_and_more'),
    ]

    operations = [
        migrations.RunPython(create_initial_data, remove_initial_data),
    ]