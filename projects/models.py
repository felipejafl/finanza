from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils.text import slugify

class ProjectStatus(models.Model):
    name = models.CharField(_('nombre'), max_length=50, unique=True)
    slug = models.SlugField(_('identificador'), max_length=50, unique=True)
    description = models.TextField(_('descripción'), blank=True)
    order = models.PositiveIntegerField(_('orden'), default=0)
    is_final = models.BooleanField(_('es estado final'), default=False, 
                                 help_text=_('Indica si es un estado que finaliza el proyecto'))
    created_at = models.DateTimeField(_('creado el'), auto_now_add=True)

    class Meta:
        verbose_name = _('estado de proyecto')
        verbose_name_plural = _('estados de proyecto')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class ProjectPriority(models.Model):
    name = models.CharField(_('nombre'), max_length=50, unique=True)
    slug = models.SlugField(_('identificador'), max_length=50, unique=True)
    description = models.TextField(_('descripción'), blank=True)
    order = models.PositiveIntegerField(_('orden'), default=0)
    color = models.CharField(_('color'), max_length=20, default='primary',
                           help_text=_('Nombre de la clase CSS para el color (ej: primary, success, danger)'))
    created_at = models.DateTimeField(_('creado el'), auto_now_add=True)

    class Meta:
        verbose_name = _('prioridad de proyecto')
        verbose_name_plural = _('prioridades de proyecto')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class TaskStatus(models.Model):
    name = models.CharField(_('nombre'), max_length=50, unique=True)
    slug = models.SlugField(_('identificador'), max_length=50, unique=True)
    description = models.TextField(_('descripción'), blank=True)
    order = models.PositiveIntegerField(_('orden'), default=0)
    is_final = models.BooleanField(_('es estado final'), default=False, 
                                 help_text=_('Indica si es un estado que finaliza la tarea'))
    created_at = models.DateTimeField(_('creado el'), auto_now_add=True)

    class Meta:
        verbose_name = _('estado de tarea')
        verbose_name_plural = _('estados de tarea')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Project(models.Model):
    title = models.CharField(_('título'), max_length=200)
    description = models.TextField(_('descripción'), blank=True)
    status = models.ForeignKey(
        ProjectStatus,
        on_delete=models.PROTECT,
        verbose_name=_('estado'),
        related_name='projects'
    )
    priority = models.ForeignKey(
        ProjectPriority,
        on_delete=models.PROTECT,
        verbose_name=_('prioridad'),
        related_name='projects'
    )
    start_date = models.DateField(_('fecha de inicio'), null=True, blank=True)
    due_date = models.DateField(_('fecha de vencimiento'), null=True, blank=True)
    is_repeatable = models.BooleanField(_('es repetible'), default=False)
    created_at = models.DateTimeField(_('creado el'), auto_now_add=True)
    updated_at = models.DateTimeField(_('actualizado el'), auto_now=True)

    class Meta:
        verbose_name = _('proyecto')
        verbose_name_plural = _('proyectos')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def completion_percentage(self):
        """Calcula el porcentaje de tareas completadas"""
        total_tasks = self.tasks.count()
        if total_tasks == 0:
            return 0
        completed_tasks = self.tasks.filter(status__is_final=True).count()
        return int((completed_tasks / total_tasks) * 100)

    def clean(self):
        if self.start_date and self.due_date and self.start_date > self.due_date:
            raise ValidationError(_('La fecha de inicio no puede ser posterior a la fecha de vencimiento'))
            
    def restart(self):
        """Reinicia el proyecto cambiando todas las tareas al estado inicial"""
        if not self.is_repeatable:
            raise ValidationError(_('Este proyecto no es repetible'))
            
        initial_status = TaskStatus.objects.filter(order=0).first()
        if not initial_status:
            raise ValidationError(_('No se encontró un estado inicial para las tareas'))
            
        self.tasks.update(status=initial_status)

class Task(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name=_('proyecto')
    )
    description = models.TextField(_('descripción'))
    status = models.ForeignKey(
        TaskStatus,
        on_delete=models.PROTECT,
        verbose_name=_('estado'),
        related_name='tasks'
    )
    due_date = models.DateField(_('fecha de vencimiento'), null=True, blank=True)
    order = models.PositiveIntegerField(
        _('orden'),
        default=0,
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(_('creado el'), auto_now_add=True)
    updated_at = models.DateTimeField(_('actualizado el'), auto_now=True)

    class Meta:
        verbose_name = _('tarea')
        verbose_name_plural = _('tareas')
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.project.title} - {self.description[:50]}"

    def clean(self):
        if self.due_date and self.project.due_date and self.due_date > self.project.due_date:
            raise ValidationError(_('La fecha de vencimiento no puede ser posterior a la del proyecto'))
