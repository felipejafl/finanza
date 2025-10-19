🖋️ Pautas de Estilo de Código en Django
1. PEP 8 como base

Seguir PEP 8
 para Python.

Indentación de 4 espacios, no tabuladores.

Nombres en inglés y descriptivos:

✅ invoice_number, ❌ inv_num, ❌ x.

Líneas ≤ 79 caracteres (o 100 como máximo).

2. Nomenclatura Django

Modelos: singular, PascalCase (User, Invoice).

Campos de modelos: snake_case (created_at, is_paid).

Vistas:

FBV: verbo + sustantivo (create_invoice, delete_user).

CBV: usar nombres genéricos (InvoiceListView, UserDetailView).

Templates:

Ubicación: templates/app_name/file.html.

Nombre claro: invoice_detail.html, user_login.html.

3. Organización de archivos

Dentro de una app:

app_name/
│── admin.py
│── apps.py
│── forms.py
│── models.py
│── serializers.py
│── services.py
│── tests/
│── urls.py
│── views.py
│── templates/app_name/


👉 Usa services.py para lógica de negocio compleja.
👉 Divide en submódulos (models/, views/) si crece demasiado.

4. Imports

Ordenados: standard library → third-party → Django → app local.

Usa isort para automatizar.

# ✅ Bien
import uuid
from datetime import datetime

import requests
from django.conf import settings
from django.db import models

from users.models import User

5. Strings y formateo

Usa f-strings en lugar de concatenación.

Para mensajes multilínea, usar textwrap.dedent o """ """.

6. Comentarios y docstrings

Clases, métodos y funciones: siempre con docstring explicativo.

Usa formato PEP 257
.

class Invoice(models.Model):
    """Modelo que representa una factura emitida al cliente."""

    number = models.CharField(max_length=20, unique=True)

7. Linting y formateo automático

Usa herramientas para mantener consistencia:

black → formateo automático.

flake8 → linting.

isort → orden de imports.

pylint-django → reglas específicas Django.

👉 Configura un pre-commit hook con estas herramientas.

8. Buenas prácticas en modelos

Siempre implementar __str__.

Validaciones en clean() o validators.

Meta ordenado (verbose_name, ordering, constraints).

9. Buenas prácticas en vistas

Mantener vistas pequeñas.

Lógica pesada en services.py o managers.py.

CBVs con mixins mejor que FBVs largas.

10. Tests

Nombres claros: test_invoice_creation_success, no test1.

Mantener fixtures de datos en conftest.py o factories.py.

11. Configuración

Separar settings/ por entorno (base.py, dev.py, prod.py).

Variables de entorno con django-environ.

No hardcodear rutas, claves ni credenciales.

12. Principios generales

KISS: mantenlo simple.

DRY: evita duplicar lógica.

YAGNI: no implementes lo que no necesitas aún.

SoC (Separation of Concerns): cada módulo con su responsabilidad clara.

✅ Resumen rápido

Sigue PEP8 + Django conventions.

Usa black + isort + flake8.

Organiza apps y módulos por dominio funcional, no por capas técnicas.

Mantén funciones y vistas cortas y legibles.

Documenta todo lo que no sea obvio.