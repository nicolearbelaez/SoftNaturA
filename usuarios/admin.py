from django.contrib import admin
from .models import Mensaje

@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ("nombre", "correo", "asunto", "fecha_envio")
    search_fields = ("nombre", "correo", "asunto")
    list_filter = ("fecha_envio",)