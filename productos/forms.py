from django import forms
from .models import Producto, Category, Calificacion


# ================================
#   FORMULARIO ÚNICO PARA PRODUCTO
#   (SIN stock NI fecha, porque van en LOTES)
# ================================
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombProduc',
            'descripcion',
            'precio',
            'Categoria',
            'imgProduc'
        ]
        labels = {
            'nombProduc': 'Nombre del producto',
            'descripcion': 'Descripción',
            'precio': 'Precio',
            'Categoria': 'Categoría',
            'imgProduc': 'Imagen',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['Categoria'].queryset = Category.objects.all()

    # VALIDACIÓN DE PRECIO
    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio is not None and precio < 0:
            raise forms.ValidationError("El precio no puede ser negativo.")
        return precio


# ================================
#     FORMULARIO DE CALIFICACIÓN
# ================================
class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = ['puntuacion_servicio', 'puntuacion_productos', 'comentario']
        widgets = {
            'puntuacion_servicio': forms.Select(
                choices=[(i, f"{i} estrella{'s' if i > 1 else ''}") for i in range(1, 6)]
            ),
            'puntuacion_productos': forms.Select(
                choices=[(i, f"{i} estrella{'s' if i > 1 else ''}") for i in range(1, 6)]
            ),
            'comentario': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Comparte tu experiencia (opcional)'})
        }


# ================================
#      FORMULARIO DE CATEGORÍA
# ================================
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['nombCategory']
        labels = {
            'nombCategory': 'Nombre de la categoría',
        }


# ================================
#          CARRITO DE COMPRAS
#   (LO DEJO AQUÍ COMO LO TENÍAS)
# ================================
class Carrito:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        carrito = self.session.get("carrito", {})
        self.carrito = carrito

    def agregar(self, producto, cantidad=1):
        producto_id = str(producto.id)
        precio_float = float(producto.precio)

        if producto_id not in self.carrito:
            self.carrito[producto_id] = {
                'producto_id': producto.id,
                'nombre': producto.nombProduc,  # corregido: el campo es 'nombProduc'
                'precio': precio_float,
                'cantidad': cantidad,
                'acumulado': precio_float * cantidad
            }
        else:
            self.carrito[producto_id]['cantidad'] += cantidad
            self.carrito[producto_id]['acumulado'] = (
                precio_float * self.carrito[producto_id]['cantidad']
            )

        self.guardar_carrito()

    def restar(self, producto):
        id_str = str(producto.id)
        if id_str in self.carrito:
            self.carrito[id_str]["cantidad"] -= 1
            self.carrito[id_str]["acumulado"] = (
                float(self.carrito[id_str]["precio"]) * self.carrito[id_str]["cantidad"]
            )

            if self.carrito[id_str]["cantidad"] <= 0:
                self.eliminar(producto)
            else:
                self.guardar_carrito()

    def eliminar(self, producto):
        id_str = str(producto.id)
        if id_str in self.carrito:
            del self.carrito[id_str]
            self.guardar_carrito()

    def guardar_carrito(self):
        self.session["carrito"] = self.carrito
        self.session.modified = True

    def limpiar(self):
        self.session["carrito"] = {}
        self.session.modified = True
