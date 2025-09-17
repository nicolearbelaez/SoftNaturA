from django.urls import path, reverse_lazy
from . import views
from django.conf import settings
from django.contrib.auth import views as auth_views

app_name = 'usuarios'

urlpatterns = [
    # Autenticación de usuarios
    path('login/', views.login_view, name="login"),
    path('register/', views.register_view, name="register"),
    path('logout/', views.logout_view, name="logout"),
    path('loginAdm/', views.loginAdmin, name="loginAdmin"),
    #Perfil de usuario
    path('editar-perfil/', views.editar_perfil, name='editar_perfil'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    # Vistas generales del sitio
    path('contacto/', views.contacto, name="contacto"),
    path('index/', views.index, name="index"),
    path('nosotros/', views.nosotros, name="nosotros"),
    # Panel de usuario / administrador
    path('dashboard/', views.dashboard, name="dashboard"),      
    path('gstUsuarios/', views.gstUsuarios, name="gstUsuarios"),
    path('cambiar_estado/<int:usuario_id>/', views.cambiar_estado_usuario, name='cambiar_estado_usuario'),
    path('agregar/', views.agregar_usuario, name='agregar_usuario'),
    path('', views.gstUsuarios, name='gstUsuarios'),
    path('informe-calificaciones/', views.informe_calificaciones, name='informe_calificaciones'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('ventas/', views.ventas_view, name="ventas"),
    path('pedidos/', views.pedidos_view, name="pedidos"),
    path('productos-mas-vendidos/', views.productos_mas_vendidos_view, name="productos_mas_vendidos"),
    path('usuarios-frecuentes/', views.usuarios_frecuentes_view, name="usuarios_frecuentes"),
    path("contacto/", views.contacto, name="contacto"),
    path('comentario/<int:id>/aprobar/', views.aprobar_comentario, name="aprobar_comentario"),
    path('comentario/<int:id>/rechazar/', views.rechazar_comentario, name="rechazar_comentario"),

    # Recuperación de contraseña
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
            email_template_name='registration/password_reset_email.html',
            success_url=reverse_lazy('usuarios:password_reset_done')
        ),
        name='password_reset'
    ),
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html',
            success_url=reverse_lazy('usuarios:password_reset_complete')
        ),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

