1. Diseño de modelos

Un modelo = una entidad del dominio (ej: User, Invoice, Order).
Nombres siempre en singular y en PascalCase (Invoice, no Invoices).
Usa verbose_name y verbose_name_plural para que se vea bien en el admin.

class Invoice(models.Model):
    number = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"

2. Campos

Usa el tipo de campo adecuado (DateTimeField, DecimalField, EmailField, etc.).
Define longitudes máximas (max_length) en CharField y TextField.
Usa null=True solo si realmente puede ser NULL en la BD (para CharField, mejor blank=True).

Valores por defecto: usar default= o funciones (default=uuid.uuid4).

3. Relaciones

Define siempre related_name en ForeignKey y ManyToManyField para claridad.
Evita relaciones circulares complicadas.

Si necesitas datos extras en una relación M2M, crea un modelo intermedio (through=).

class Order(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="orders")

class Product(models.Model):
    name = models.CharField(max_length=200)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

4. Métodos de modelo

Implementa __str__ en todos los modelos para debug y admin.

Métodos que representen lógica de negocio inmediata (ej: is_paid, total_amount).
Métodos que afecten varias entidades → mover a services.py.

class Invoice(models.Model):
    number = models.CharField(max_length=20, unique=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Invoice {self.number}"

    def mark_as_paid(self):
        self.is_paid = True
        self.save(update_fields=["is_paid"])

5. Managers y QuerySets

Usa managers personalizados (objects = MyManager()) para queries comunes.
Agrupa lógica de acceso a BD en Managers/QuerySets, no en vistas.

class PaidInvoiceQuerySet(models.QuerySet):
    def paid(self):
        return self.filter(is_paid=True)

class Invoice(models.Model):
    number = models.CharField(max_length=20)
    is_paid = models.BooleanField(default=False)

    objects = PaidInvoiceQuerySet.as_manager()

6. Migrations

Haz migraciones pequeñas y frecuentes (makemigrations + migrate).
Nombra las migraciones de forma clara (python manage.py makemigrations --name add_invoice_number).
Evita cambios destructivos en producción (elimina campos/tablas solo tras plan).

7. Integridad y constraints

Usa unique=True o UniqueConstraint en Meta.
Para validaciones complejas, usa CheckConstraint.
Mantén la integridad referencial (on_delete=models.CASCADE/PROTECT/SET_NULL).

class Product(models.Model):
    sku = models.CharField(max_length=20, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(price__gte=0), name="price_non_negative"),
        ]

8. Optimización

Usa select_related y prefetch_related para evitar el problema N+1 queries.
Indexa campos que se usan en filtros (db_index=True).
Para búsquedas full-text usa Postgres + SearchVector o Elastic.

9. Buenas prácticas de mantenimiento

Documenta con docstrings qué representa cada modelo.
Mantén los modelos pequeños (si crecen mucho, separa en varios archivos dentro de models/).
No mezcles lógica de negocio pesada aquí → mejor services/.

10. Admin de Django

Registra todos los modelos en admin.py.
Usa list_display, search_fields, list_filter.
Admins personalizados para mejorar productividad.