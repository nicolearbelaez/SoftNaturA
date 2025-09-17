from django.shortcuts import render,  get_object_or_404, redirect
from .forms import registerProduc
from .models import Producto, Category
from .forms import Carrito
from django.urls import reverse
from usuarios.decorators import admin_required
from .forms import ProductoForm, CategoriaForm
from django.db.models import Q
import openpyxl
from django.http import HttpResponse
from .models import Servicio, Calificacion
from usuarios.models import Usuario , Pedido
from .models import CarritoItem



# Create your views here.

def productos(request):
    products = Producto.objects.all()
    return render(request, 'productos/producto.html', {'products': products})

@admin_required
def list_produc(request):
    return render(request, 'productos/list_produc.html')

@admin_required
def registerProducts(request):
    productos = Producto.objects.all()
    form = ProductoForm()  # 👈 Aquí se usa el formulario corregido

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('productos:listProduc')

    return render(request, 'productos/list_produc.html', {
        'form': form,
        'productos': productos
    })

@admin_required
def list_product(request):
    productos = Producto.objects.all()
    return render(request, 'productos/list_produc.html', {'productos': productos}) 

def producto(request):
    return render(request, "todo/producto.html", {"usuario_id": request.user})


def productos_view(request, categoria_id=None):
    buscar = request.GET.get('buscar', '')  # 👈 corregido, antes decía 'q'

    if categoria_id:
        try:
            categoria = Category.objects.get(id=categoria_id)
            productos = Producto.objects.filter(categoria=categoria, estado=True)
        except Category.DoesNotExist:
            productos = Producto.objects.filter(estado=True)
            categoria = None
    else:
        productos = Producto.objects.filter(estado=True)
        categoria = None

    # 🔎 Aplicar búsqueda
    if buscar:
        productos = productos.filter(
            Q(nombProduc__icontains=buscar) |
            Q(descripcion__icontains=buscar)
        )

    # Carrito en sesión
    carrito = request.session.get('carrito', {})
    items = []
    subtotal = 0
    total_cantidad = 0

    for key, value in carrito.items():
        if not isinstance(value, dict):
            continue

        cantidad = int(value.get("cantidad", 0))
        precio = float(value.get("precio", 0))
        nombre = value.get("nombProduc", "Sin nombre")
        precio_total = cantidad * precio

        subtotal += precio_total
        total_cantidad += cantidad

        items.append({
            "producto_id": key,
            "producto": nombre,
            "cantidad": cantidad,
            "precio_unitario": precio,
            "precio_total": precio_total
        })

    iva = subtotal * 0.19
    total = subtotal + iva

    categorias = Category.objects.all()

    return render(request, 'productos/producto.html', {
        'products': productos,
        'carrito': items,
        'subtotal': round(subtotal, 2),
        'iva': round(iva, 2),
        'total': round(total, 2),
        'total_cantidad': total_cantidad,
        'categorias': categorias,
        'categoria_actual': categoria,
        'buscar': buscar,  # 👈 importante para mantener lo que escribió el usuario
    })

def agregarAlCarrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    producto = Producto.objects.get(id=producto_id)
    producto_id_str = str(producto_id)

    # ✅ Actualizamos el carrito en sesión
    if producto_id_str in carrito:
        carrito[producto_id_str]["cantidad"] += 1
    else:
        carrito[producto_id_str] = {
            "cantidad": 1,
            "precio": float(producto.precio),
            "nombProduc": producto.nombProduc,
            "imgProduc": producto.imgProduc.url

        }

    request.session['carrito'] = carrito
    request.session.modified = True

    # ✅ Guardar también en la base de datos si el usuario está logueado
    usuario_id = request.session.get("usuario_id")
    if usuario_id:
        item, creado = CarritoItem.objects.get_or_create(
            usuario_id=usuario_id,
            producto=producto
        )
        item.cantidad = carrito[producto_id_str]["cantidad"]
        item.save()

    return redirect(f"{reverse('productos:producto')}?carrito=1")

def eliminar(request, producto_id):
    carrito = request.session.get('carrito', {})
    producto_id_str = str(producto_id)

    if producto_id_str in carrito:
        del carrito[producto_id_str]

    request.session['carrito'] = carrito
    request.session.modified = True
    return redirect("productos:producto")


def restar_producto(request, producto_id):
    carrito = request.session.get('carrito', {})
    producto_id_str = str(producto_id)
    usuario_id = request.session.get("usuario_id")

    if producto_id_str in carrito:
        if carrito[producto_id_str]["cantidad"] > 1:
            carrito[producto_id_str]["cantidad"] -= 1

            # ✅ Actualizar en BD si el usuario está logueado
            if usuario_id:
                CarritoItem.objects.filter(
                    usuario_id=usuario_id, producto_id=producto_id
                ).update(cantidad=carrito[producto_id_str]["cantidad"])

        else:
            del carrito[producto_id_str]

            # ✅ Eliminar de BD si el usuario está logueado
            if usuario_id:
                CarritoItem.objects.filter(
                    usuario_id=usuario_id, producto_id=producto_id
                ).delete()

    request.session['carrito'] = carrito
    request.session.modified = True
    return redirect(f"{reverse('productos:producto')}?carrito=1")


def limpiar(request):
    request.session['carrito'] = {}
    request.session.modified = True
    return redirect("productos:producto")

def checkout(request):
    carrito = request.session.get("carrito", {})
    productos = []
    total = 0

    for item in carrito.values():
        imagen = item.get('imgProduc', '')
        nombre = item.get('nombProduc', 'Sin nombre')
        cantidad = int(item.get('cantidad', 0))
        precio = float(item.get('precio', 0))
        subtotal = precio * cantidad
        total += subtotal

        productos.append({
            'imagen': imagen,
            'nombre': nombre,
            'cantidad': cantidad,
            'precio': precio,
            'subtotal': subtotal
        })

    # ✅ Calcular IVA (19%)
    iva = total * 0.19
    total_con_iva = total + iva

    # ✅ Guardar pedido en la base de datos
    if request.user.is_authenticated:
        pedido = Pedido.objects.create(
            usuario=request.user,
            total=total_con_iva,
            estado="pendiente"  # luego lo puedes cambiar a "pagado"
        )

    return render(request, 'productos/checkout.html', {
        'productos': productos,
        'total': total,
        'iva': iva,
        'total_con_iva': total_con_iva
    })

@admin_required
def agregar_producto(request):
    form = ProductoForm(request.POST or None, request.FILES or None)
    productos = Producto.objects.all()

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('productos:agregar_producto')

    return render(request, 'productos/agregar_producto.html', {
        'form': form,
        'productos': productos
    })

@admin_required
def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('productos:list_product')  # Asegúrate que este nombre esté en tu urls.py
    else:
        form = ProductoForm(instance=producto)

    return render(request, 'productos/editar_producto.html', {'form': form, 'producto': producto})

@admin_required
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    producto.delete()
    return redirect('productos:list_product')  # Ajusta si tu URL se llama distinto
def productos_por_categoria(request, categoria_id):
    try:
        categoria = Category.objects.get(id=categoria_id)
        # IMPORTANTE: Aquí filtras los productos por la categoría seleccionada
        productos = Producto.objects.filter(Categoria=categoria, estado=True)
    except Category.DoesNotExist:
        productos = Producto.objects.filter(estado=True)
        categoria = None
    
    # Código del carrito (igual que tu vista original)
    usuario_id = request.session.get('usuario_id')
    
    carrito = request.session.get('carrito', {})
    items = []
    total = 0
    
    for key, value in carrito.items():
        if not isinstance(value, dict):
            continue
            
        cantidad = int(value.get("cantidad", 0))
        precio = float(value.get("precio", 0))
        nombre = value.get("nombProduc", "Sin nombre")
        
        subtotal = precio * cantidad
        items.append({
            "producto": nombre,
            "cantidad": cantidad,
            "precio": precio,
            "subtotal": subtotal
        })
        total += subtotal
    
    categorias = Category.objects.all()
    
    return render(request, 'productos/producto.html', {
        'products': productos,  
        'usuario_id': usuario_id,
        'carrito': items,
        'total': total,
        'categorias': categorias,
        'categoria_actual': categoria,
    })

@admin_required
def exportar_inventario_excel(request):
    # Crear libro y hoja
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Inventario'

    # Encabezados
    ws.append(['Nombre', 'Descripción', 'Precio', 'Stock', 'Categoría'])

    # Agregar productos
    productos = Producto.objects.all()
    for producto in productos:
        ws.append([
            producto.nombProduc,
            producto.descripcion,
            float(producto.precio),
            producto.stock,
            str(producto.Categoria)
        ])

    # Crear respuesta
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Inventario.xlsx'
    wb.save(response)
    return response

@admin_required
def activar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    producto.estado = True
    producto.save()
    return redirect('productos:listProduc')

@admin_required
def inactivar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    producto.estado = False
    producto.save()
    return redirect('productos:listProduc')


def guardar_calificacion(request):
    if request.method == 'POST':
        servicio_id = request.POST.get('servicio_id')
        puntuacion_servicio = request.POST.get('puntuacion_servicio')
        puntuacion_productos = request.POST.get('puntuacion_productos')
        comentario = request.POST.get('comentario')

        print("Datos recibidos:")
        print("servicio_id:", servicio_id)
        print("puntuacion_servicio:", puntuacion_servicio)
        print("puntuacion_productos:", puntuacion_productos)
        print("comentario:", comentario)

        try:
            servicio = Servicio.objects.get(id=servicio_id)
        except Servicio.DoesNotExist:
            return HttpResponse("❌ Servicio no encontrado", status=404)

        usuario_obj = request.user

        calificacion = Calificacion.objects.create(
            servicio=servicio,
            usuario=usuario_obj,
            puntuacion_servicio=int(puntuacion_servicio),
            puntuacion_productos=int(puntuacion_productos),
            comentario=comentario
        )

        print("✅ Calificación guardada:", calificacion)

        return render(request, 'productos/correctamente.html')

    return HttpResponse("❌ Método no permitido", status=405)


def correctamente(request):
    return render (request, 'productos/correctamente.html')

def cargar_carrito_usuario(request, usuario):
    carrito_items = CarritoItem.objects.filter(usuario=usuario)
    carrito = {}

    for item in carrito_items:
        carrito[str(item.producto.id)] = {
            "cantidad": item.cantidad,
            "precio": float(item.producto.precio),
            "nombProduc": item.producto.nombProduc,
        }

    request.session["carrito"] = carrito
    request.session.modified = True


def agregar_categoria(request):
    form = CategoriaForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect('productos:agregar_categoria')  # se queda en la misma página
    categorias = Category.objects.all()
    return render(request, 'productos/list_produc.html', {
        'form': form,
        'categorias': categorias
    })

def homeSoft(request):
    mas_vendidos = Producto.objects.filter(estado=True).order_by("vendidos")[:3]
    comentarios = Calificacion.objects.filter(aprobado=True).order_by('-fecha_creacion')
    return render(request, "productos/homeSoft.html", {
        "mas_vendidos": mas_vendidos,
        "comentarios": comentarios
        })

def aprobar_comentario(request, id):
    calificacion = get_object_or_404(Calificacion, id=id)
    calificacion.aprobado = True
    calificacion.save()
    return redirect('productos:informe_calificaciones')

def rechazar_comentario(request,id):
    calificacion = get_object_or_404(Calificacion, id=id)
    calificacion.delete()
    return redirect('productos:informe_calificaciones')