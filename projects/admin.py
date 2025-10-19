# Este archivo ya no es necesario si no usas el admin de Django.
# Puedes eliminarlo completamente.
# from django.contrib import admin
# from .models import Project, Task, ProjectStatus, ProjectPriority, TaskStatus
# from django.utils.translation import gettext_lazy as _

# @admin.register(ProjectStatus)
# class ProjectStatusAdmin(admin.ModelAdmin):
#     list_display = ('name', 'order', 'is_final')
#     search_fields = ('name', 'description')
#     prepopulated_fields = {'slug': ('name',)}

# @admin.register(ProjectPriority)
# class ProjectPriorityAdmin(admin.ModelAdmin):
#     list_display = ('name', 'order', 'color')
#     search_fields = ('name', 'description')
#     prepopulated_fields = {'slug': ('name',)}

# @admin.register(Project)
# class ProjectAdmin(admin.ModelAdmin):
#     list_display = ('title', 'status', 'priority', 'start_date', 'due_date', 'is_repeatable', 'completion_percentage')
#     list_filter = ('status', 'priority', 'is_repeatable')
#     search_fields = ('title', 'description')
#     date_hierarchy = 'created_at'

# @admin.register(Task)
# class TaskAdmin(admin.ModelAdmin):
#     list_display = ('project', 'description', 'status', 'due_date', 'order')
#     list_filter = ('status', 'project')
#     search_fields = ('description', 'project__title')
#     date_hierarchy = 'created_at'

# @admin.register(TaskStatus)
# class TaskStatusAdmin(admin.ModelAdmin):
#     list_display = ('name', 'order', 'is_final')
#     search_fields = ('name', 'description')
#     prepopulated_fields = {'slug': ('name',)}
