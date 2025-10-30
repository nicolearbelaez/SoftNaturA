
from django.contrib import admin
from django.urls import path, include
from . import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls', namespace='usuarios')),
    path('pagos/', include('pagos.urls')),
    path('', include ('productos.urls', namespace='productos')),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)