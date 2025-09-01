from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date

# Create your models here.
class Category(models.Model):
    nombCategory = models.CharField(max_length=140)
    def __str__(self):
        return self.nombCategory
    class Meta:
        verbose_name_plural = 'Categoria'

class Producto(models.Model):
    nombProduc = models.CharField(max_length=130)
    descripcion = models.CharField(max_length=300)
    Categoria = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imgProduc = models.ImageField(upload_to='uploads/products/')
    stock = models.IntegerField(default=0)  # ✅ Nuevo campo
    estado = models.BooleanField(default=True)  # True = Activo, False = Inactivo
    fecha_caducidad = models.DateField(null=True, blank=True)  # ⬅️ Campo de fecha de vencimiento

    def esta_vencido(self):
        if self.fecha_caducidad:
            return date.today() > self.fecha_caducidad
        return False
    def __str__(self):
        return self.nombProduc


class Servicio(models.Model):
    TIPO_CHOICES = [
        ('compra', 'Compra')
    ]
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)

    def __str__(self):
        return self.nombre

class Calificacion(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='calificaciones')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    puntuacion_servicio = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    puntuacion_productos = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.servicio.nombre} - {self.puntuacion_servicio} / {self.puntuacion_productos}'

class CarritoItem(models.Model):
    usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE)  # ✅ Usar string
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('usuario', 'producto')

    def __str__(self):
        return f"{self.producto.nombProduc} x {self.cantidad}"