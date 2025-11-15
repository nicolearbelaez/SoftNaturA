from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'productos'

urlpatterns = [
    path('', views.productos_view, name="producto"),
    path('gstproduct/', views.registerProducts, name="listProduc"),
    path('agregar/<int:producto_id>/', views.agregarAlCarrito, name="agregar"),
    path('restar/<int:producto_id>/', views.restar_producto, name='restar'),
    path('limpiar/', views.limpiar, name="limpiar"),
    path('agregar/', views.agregar_producto, name='agregar_producto'),
    path('editar/<int:id>/', views.editar_producto, name='editar_producto'),
    path('list_produc/', views.list_product, name='list_product'),
    path('categoria/<int:categoria_id>/', views.productos_por_categoria, name='productos_por_categoria'),
    path('exportar_excel/', views.exportar_inventario_excel, name='exportar_excel'),
    path('activar/<int:id>/', views.activar_producto, name='activar_producto'),
    path('inactivar/<int:id>/', views.inactivar_producto, name='inactivar_producto'),
    path('guardar-calificacion/', views.guardar_calificacion, name='guardar_calificacion'),
    path('agregar_categoria/', views.agregar_categoria, name='agregar_categoria'),
    path("categorias/", views.listar_categorias, name="listar_categorias"),
    path("categorias/editar/<int:id>/", views.editar_categoria, name="editar_categoria"),
    path("categorias/eliminar/<int:id>/", views.eliminar_categoria, name="eliminar_categoria"),
    path('homesoft/', views.homeSoft, name="homesoft"),
    path('devoluciones/', views.devoluciones, name='devoluciones'),
    path("producto/<int:pk>/", views.detalle_producto, name="detalle"),
    path("chatbot/ask/", views.chatbot_ajax, name="chatbot_ajax"),




]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
