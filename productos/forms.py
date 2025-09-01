from django import forms
from .models import Producto, Category
from .models import Calificacion


class registerProduc(forms.Form):
    nombProduc = forms.CharField(max_length=130)
    descripcion = forms.CharField(max_length=80)
    Categoria = forms.ModelChoiceField(queryset=Category.objects.all())
    precio = forms.DecimalField(max_digits=10, decimal_places=2)
    imgProduc = forms.ImageField()

    def __init__(self, *args, **kwargs):
        super(registerProduc, self).__init__(*args, **kwargs)
        self.fields['Categoria'].queryset = Category.objects.all()  # Se carga correctamente al instanciar

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
                'nombre': producto.nombre, # O 'nombProduc' si ese es el campo
                'precio': precio_float,
                'cantidad': cantidad,
                'acumulado': precio_float * cantidad # <-- ¡CRÍTICO: INICIALIZA ESTO!
            }
        else:
            self.carrito[producto_id]['cantidad'] += cantidad
            self.carrito[producto_id]['acumulado'] += precio_float * cantidad # <-- Y RECALCULA ESTO (no solo suma precio_float)
        # O mejor: self.carrito[producto_id]['acumulado'] = precio_float * self.carrito[producto_id]['cantidad']
        self.guardar_carrito()

    def restar(self, producto):
        id_str = str(producto.id)
        if id_str in self.carrito:
            self.carrito[id_str]["cantidad"] -= 1
            # Recalcula el acumulado para este ítem
            self.carrito[id_str]["acumulado"] = float(self.carrito[id_str]["precio"]) * self.carrito[id_str]["cantidad"]

            if self.carrito[id_str]["cantidad"] <= 0:
                self.eliminar(producto)
            else:
                self.guardar_carrito() # Guarda si no se eliminó

    def eliminar(self, producto):
        id_str = str(producto.id)
        if id_str in self.carrito:
            del self.carrito[id_str]
            self.guardar_carrito()

    def guardar_carrito(self):
        self.session["carrito"] = self.carrito
        self.session.modified = True # ¡Esto es CRUCIAL para que Django guarde los cambios!

    def limpiar(self):
        self.session["carrito"] = {}
        self.session.modified = True



class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombProduc', 'descripcion', 'precio', 'Categoria', 'imgProduc', 'stock', 'fecha_caducidad']
        labels = {
            'nombProduc': 'Nombre del producto',
            'descripcion': 'Descripción',
            'precio': 'Precio',
            'Categoria': 'Categoría',
            'imgProduc': 'Imagen',
            'stock': 'Cantidad en stock',
        }

    def __init__(self, *args, **kwargs):
        super(ProductoForm, self).__init__(*args, **kwargs)
        self.fields['Categoria'].queryset = Category.objects.all()

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is not None and stock < 0:
            raise forms.ValidationError("El stock no puede ser negativo.")
        return stock

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio is not None and precio < 0:
            raise forms.ValidationError("El precio no puede ser negativo.")
        return precio

class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = ['puntuacion_servicio', 'puntuacion_productos', 'comentario']
        widgets = {
            'puntuacion_servicio': forms.Select(choices=[(i, f'{i} estrella{"s" if i > 1 else ""}') for i in range(1, 6)]),
            'puntuacion_productos': forms.Select(choices=[(i, f'{i} estrella{"s" if i > 1 else ""}') for i in range(1, 6)]),
            'comentario': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Comparte tu experiencia (opcional)'})
        }

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['nombCategory']
        labels = {
            'nombCategory': 'Nombre de la categoría',
        }