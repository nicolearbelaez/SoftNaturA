from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings

class Transaccion(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
        ('pending', 'Pendiente de confirmación'),
    ]
    
    order_id = models.CharField(max_length=100, unique=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    pedido = models.ForeignKey('usuarios.Pedido', on_delete=models.SET_NULL, null=True, blank=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # Datos de Bold
    bold_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    bold_response = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return f"Transacción {self.order_id} - {self.estado}"
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Transacción'
        verbose_name_plural = 'Transacciones'