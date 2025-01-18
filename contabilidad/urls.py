from django.urls import path
from .views import (
    inicio,
    cuenta_listar,
    cuenta_crear,
    cuenta_editar,
    cuenta_eliminar,
    TransaccionListAPIView,
    transaccion_listar,
    transaccion_crear,
    transaccion_editar,
    transaccion_eliminar,
    importar_datos,
    categoria_listar,
    categoria_crear,
    categoria_editar,
    categoria_eliminar,
    reporte_balance_general,
    reporte_estado_resultados,
    reporte_presupuesto_mensual,
    presupuesto_listar,
    presupuesto_crear,
    presupuesto_editar,
    presupuesto_eliminar,
)

urlpatterns = [
    path('', inicio, name='inicio'),

    path('cuentas/', cuenta_listar, name='cuenta_listar'),
    path('cuentas/crear/', cuenta_crear, name='cuenta_crear'),
    path('cuentas/<int:pk>/editar/', cuenta_editar, name='cuenta_editar'),
    path('cuentas/<int:pk>/eliminar/', cuenta_eliminar, name='cuenta_eliminar'),

    path('transacciones/', transaccion_listar, name='transaccion_listar'),
    path('api/transacciones/', TransaccionListAPIView.as_view(), name='transaccion-api'),
    path('transacciones/crear/', transaccion_crear, name='transaccion_crear'),
    path('transacciones/<int:pk>/editar/', transaccion_editar, name='transaccion_editar'),
    path('transacciones/<int:pk>/eliminar/', transaccion_eliminar, name='transaccion_eliminar'),
    path('transacciones/importar/', importar_datos, name='importar_datos'),

    path('presupuestos/', presupuesto_listar, name='presupuesto_listar'),
    path('presupuestos/crear/', presupuesto_crear, name='presupuesto_crear'),
    path('presupuestos/<int:pk>/editar/', presupuesto_editar, name='presupuesto_editar'),
    path('presupuestos/<int:pk>/eliminar/', presupuesto_eliminar, name='presupuesto_eliminar'),

    path('categorias/', categoria_listar, name='categoria_listar'),
    path('categorias/crear/', categoria_crear, name='categoria_crear'),
    path('categorias/<int:pk>/editar/', categoria_editar, name='categoria_editar'),
    path('categorias/<int:pk>/eliminar/', categoria_eliminar, name='categoria_eliminar'),

    path('reportes/balance-general/', reporte_balance_general, name='reporte_balance_general'),
    path('reportes/estado-resultados/', reporte_estado_resultados, name='reporte_estado_resultados'),
    path('reportes/presupuesto-mensual/', reporte_presupuesto_mensual, name='reporte_presupuesto_mensual'),
]
