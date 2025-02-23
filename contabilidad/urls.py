from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

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
    categoria_listar,
    categoria_crear,
    categoria_editar,
    categoria_eliminar,
    reporte_presupuesto_mensual,
    reporte_financiero,
    reporte_gastos_por_categoria,
    reporte_saldo_cuentas_dinamico,
    reporte_transacciones_filtrado,
    resumen_ingresos_por_tipo,
    reporte_gastos_deducibles,
    reporte_iva,
    reporte_retenciones_irpf,
    presupuesto_listar,
    presupuesto_crear,
    presupuesto_editar,
    presupuesto_eliminar,
    cargar_ticket,
    guardar_transacciones,
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
    path('transacciones/cargar_ticket/', cargar_ticket, name='cargar_ticket'),
    path('transacciones/resultado/', guardar_transacciones, name='guardar_transacciones'),

    path('presupuestos/', presupuesto_listar, name='presupuesto_listar'),
    path('presupuestos/crear/', presupuesto_crear, name='presupuesto_crear'),
    path('presupuestos/<int:pk>/editar/', presupuesto_editar, name='presupuesto_editar'),
    path('presupuestos/<int:pk>/eliminar/', presupuesto_eliminar, name='presupuesto_eliminar'),

    path('categorias/', categoria_listar, name='categoria_listar'),
    path('categorias/crear/', categoria_crear, name='categoria_crear'),
    path('categorias/<int:pk>/editar/', categoria_editar, name='categoria_editar'),
    path('categorias/<int:pk>/eliminar/', categoria_eliminar, name='categoria_eliminar'),

    path('reportes/presupuesto-mensual/', reporte_presupuesto_mensual, name='reporte_presupuesto_mensual'),
    path('reportes/reporte_financiero/', reporte_financiero, name='reporte_financiero'),
    path('reportes/reporte_gastos_categoria/', reporte_gastos_por_categoria, name='reporte_gastos_categoria'),
    path('reportes/reporte_saldo_cuentas_dinamico/', reporte_saldo_cuentas_dinamico, name='reporte_saldo_cuentas_dinamico'),
    path('reportes/reporte_transacciones_filtrado/', reporte_transacciones_filtrado, name='reporte_transacciones_filtrado'),
    path('reportes/resumen_ingresos_por_tipo/', resumen_ingresos_por_tipo, name='resumen_ingresos_por_tipo'),
    path('reportes/reporte_gastos_deducibles/', reporte_gastos_deducibles, name='reporte_gastos_deducibles'),
    path('reportes/reporte_iva/', reporte_iva, name='reporte_iva'),
    path('reportes/reporte_retenciones_irpf/', reporte_retenciones_irpf, name='reporte_retenciones_irpf'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
