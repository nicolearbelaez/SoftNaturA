from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date
from cloudinary.models import CloudinaryField

# Create your models here.
class Category(models.Model):
    nombCategory = models.CharField(max_length=140)
    def __str__(self):
        return self.nombCategory
    class Meta:
        verbose_name_plural = 'Categoria'

from django.db import models
from datetime import date, timedelta
from cloudinary.models import CloudinaryField


class Producto(models.Model):
    nombProduc = models.CharField(max_length=130)
    descripcion = models.CharField(max_length=300)
    Categoria = models.ForeignKey('Category', on_delete=models.CASCADE, default=1)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imgProduc = CloudinaryField('image')
    estado = models.BooleanField(default=True)  # True = Activo, False = Inactivo
    vendidos = models.IntegerField(default=0)

    def __str__(self):
        return self.nombProduc

    # --------------------------
    #   CÁLCULO DE STOCK REAL
    # --------------------------
    @property
    def stock_total(self):
        """Suma todas las cantidades de los lotes disponibles."""
        return sum(lote.cantidad for lote in self.lotes.all())

    # --------------------------
    #   LOTE MÁS PRÓXIMO A VENCER
    # --------------------------
    @property
    def vencimiento_cercano(self):
        lote = self.lotes.order_by("fecha_caducidad").first()
        return lote.fecha_caducidad if lote else None

    # --------------------------
    #   ESTADO: VENCIDO
    # --------------------------
    @property
    def esta_vencido(self):
        fecha = self.vencimiento_cercano
        return fecha and date.today() > fecha

    # --------------------------
    #   ESTADO: POR VENCER (10 días)
    # --------------------------
    @property
    def esta_por_vencerse(self):
        fecha = self.vencimiento_cercano
        if fecha:
            hoy = date.today()
            return hoy >= fecha - timedelta(days=10) and hoy < fecha
        return False

    
class Lote(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="lotes")
    codigo_lote = models.CharField(max_length=50)
    fecha_caducidad = models.DateField()
    cantidad = models.IntegerField()

    def __str__(self):
        return f"{self.producto.nombProduc} - {self.codigo_lote}"


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
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='calificaciones', null=True, blank=True)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='calificaciones', null=True, blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    puntuacion_servicio = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    puntuacion_productos = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    aprobado = models.BooleanField(default=False)

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