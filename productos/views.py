from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.db.models import Q
from django.contrib import messages
import openpyxl
from django.utils import timezone
from datetime import timedelta

from .forms import registerProduc, Carrito, ProductoForm, CategoriaForm
from .models import Producto, Category, Servicio, Calificacion, CarritoItem
from usuarios.models import Usuario, Pedido, PedidoItem
from usuarios.decorators import admin_required
from usuarios.models import Devolucion, Pedido  # Importar de usuarios
from usuarios.decorators import login_required


# ---------------------- VISTAS DE PRODUCTOS ----------------------

def productos(request):
    products = Producto.objects.all()
    return render(request, 'productos/producto.html', {'products': products})


@admin_required
def list_produc(request):
    return render(request, 'productos/list_produc.html')


@admin_required
def registerProducts(request):
    productos = Producto.objects.all()
    form = ProductoForm()

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



def productos_view(request, categoria_id=None):
    buscar = request.GET.get('buscar', '')

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

    if buscar:
        productos = productos.filter(
            Q(nombProduc__icontains=buscar) |
            Q(descripcion__icontains=buscar)
        )

    # ------------------ Carrito en sesión ------------------
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
        'buscar': buscar,
    })


# ---------------------- CARRITO ----------------------

def agregarAlCarrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = request.session.get("carrito", {})
    producto_id_str = str(producto.id)

    # --- SESIÓN ---
    if producto_id_str in carrito:
        carrito[producto_id_str]["cantidad"] += 1
    else:
        carrito[producto_id_str] = {
            "cantidad": 1,
            "precio": float(producto.precio),
            "nombProduc": producto.nombProduc,
            "imgProduc": producto.imgProduc.url
        }

    request.session["carrito"] = carrito
    request.session.modified = True

    # --- BASE DE DATOS (si el usuario está logueado) ---
    if request.user.is_authenticated:
        item, creado = CarritoItem.objects.get_or_create(
            usuario=request.user,
            producto=producto
        )
        if not creado:
            item.cantidad += 1
        item.save()

    return redirect(f"{reverse('productos:producto')}?carrito=1")


def eliminar(request, producto_id):
    carrito = request.session.get('carrito', {})
    producto_id_str = str(producto_id)

    # --- SESIÓN ---
    if producto_id_str in carrito:
        del carrito[producto_id_str]

    request.session['carrito'] = carrito
    request.session.modified = True

    # --- BASE DE DATOS ---
    if request.user.is_authenticated:
        CarritoItem.objects.filter(usuario=request.user, producto_id=producto_id).delete()

    return redirect("productos:producto")


def restar_producto(request, producto_id):
    carrito = request.session.get('carrito', {})
    producto_id_str = str(producto_id)

    # --- SESIÓN ---
    if producto_id_str in carrito:
        if carrito[producto_id_str]["cantidad"] > 1:
            carrito[producto_id_str]["cantidad"] -= 1
        else:
            del carrito[producto_id_str]

    request.session['carrito'] = carrito
    request.session.modified = True

    # --- BASE DE DATOS ---
    if request.user.is_authenticated:
        try:
            item = CarritoItem.objects.get(usuario=request.user, producto_id=producto_id)
            if item.cantidad > 1:
                item.cantidad -= 1
                item.save()
            else:
                item.delete()
        except CarritoItem.DoesNotExist:
            pass

    return redirect(f"{reverse('productos:producto')}?carrito=1")


def limpiar(request):
    # --- SESIÓN ---
    request.session['carrito'] = {}
    request.session.modified = True

    # --- BASE DE DATOS ---
    if request.user.is_authenticated:
        CarritoItem.objects.filter(usuario=request.user).delete()

    return redirect("productos:producto")


# ---------------------- CRUD PRODUCTOS ----------------------

@admin_required
def agregar_producto(request):
    form = ProductoForm(request.POST or None, request.FILES or None)
    productos = Producto.objects.all()

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('productos:agregar_producto')

    return render(request, 'productos/list_produc.html', {
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
            return redirect('productos:list_product')
    else:
        form = ProductoForm(instance=producto)

    return render(request, 'productos/editar_producto.html', {'form': form, 'producto': producto})

def productos_por_categoria(request, categoria_id):
    try:
        categoria = Category.objects.get(id=categoria_id)
        productos = Producto.objects.filter(Categoria=categoria, estado=True)
    except Category.DoesNotExist:
        productos = Producto.objects.filter(estado=True)
        categoria = None

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


# ---------------------- INVENTARIO / EXPORTAR ----------------------

@admin_required
def exportar_inventario_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Inventario'

    ws.append(['Nombre', 'Descripción', 'Precio', 'Stock', 'Categoría'])

    productos = Producto.objects.all()
    for producto in productos:
        ws.append([
            producto.nombProduc,
            producto.descripcion,
            float(producto.precio),
            producto.stock,
            str(producto.Categoria)
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Inventario_de_productos.xlsx'
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


# ---------------------- CALIFICACIONES ----------------------
def guardar_calificacion(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')   # ✅ viene del formulario
        puntuacion_servicio = request.POST.get('puntuacion_servicio')
        puntuacion_productos = request.POST.get('puntuacion_productos')
        comentario = request.POST.get('comentario')

        print("Datos recibidos:")
        print("producto_id:", producto_id)
        print("puntuacion_servicio:", puntuacion_servicio)
        print("puntuacion_productos:", puntuacion_productos)
        print("comentario:", comentario)

        try:
            producto = Producto.objects.get(id=producto_id)  # ✅ ya no busca Servicio
        except Producto.DoesNotExist:
            return HttpResponse("❌ Producto no encontrado", status=404)

        usuario_obj = request.user

        Calificacion.objects.create(
            producto=producto,                 # ✅ guarda asociado al producto
            usuario=usuario_obj,
            puntuacion_servicio=int(puntuacion_servicio),
            puntuacion_productos=int(puntuacion_productos),
            comentario=comentario
        )

        print("✅ Calificación guardada correctamente")

        return render(request, 'productos/homeSoft.html')

    return HttpResponse("❌ Método no permitido", status=405)



# ---------------------- CARGAR CARRITO USUARIO ----------------------

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


# ---------------------- CRUD CATEGORÍAS ----------------------

@admin_required
def agregar_categoria(request):
    if request.method == "POST":
        nombre = request.POST.get("nombCategory")
        if nombre:
            Category.objects.create(nombCategory=nombre)
    return redirect('productos:listar_categorias')


@admin_required
def editar_categoria(request, id):
    categoria = get_object_or_404(Category, id=id)
    if request.method == "POST":
        nuevo_nombre = request.POST.get("nombre")
        if nuevo_nombre:
            categoria.nombCategory = nuevo_nombre
            categoria.save()
    return redirect('productos:listar_categorias')


@admin_required
def listar_categorias(request):
    categorias = Category.objects.all()
    productos = Producto.objects.all()
    form = CategoriaForm()

    if request.method == "POST":
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('productos:listar_categorias')

    return render(request, 'productos/list_produc.html', {
        'categorias': categorias,
        'productos': productos,
        'form': form
    })


@admin_required
def eliminar_categoria(request, id):
    categoria = get_object_or_404(Category, id=id)
    categoria.delete()
    return redirect('productos:listar_categorias')


# ---------------------- HOME ----------------------

def homeSoft(request):
    mas_vendidos = Producto.objects.filter(estado=True).order_by("vendidos")[:3]
    comentarios = Calificacion.objects.filter(aprobado=True).order_by('-fecha_creacion')
    return render(request, "productos/homeSoft.html", {
        "mas_vendidos": mas_vendidos,
        "comentarios": comentarios
    })

# ========== IMPORTS PARA VISTA DE DEVOLUCIONES ==========                                                                                                                                     
@login_required
def devoluciones(request):
    """Vista para que el cliente solicite devoluciones"""
    
    # ✅ CORREGIDO: Solo pedidos ENTREGADOS de los últimos 30 días
    hace_30_dias = timezone.now() - timedelta(days=30)
    
    pedidos = Pedido.objects.filter(
        usuario=request.user,
        estado='entregado',  # ✅ SOLO ENTREGADOS
        fecha_creacion__gte=hace_30_dias  # ✅ ÚLTIMOS 30 DÍAS
    ).prefetch_related('items__producto').order_by('-fecha_creacion')
    
    # Preparar lista de productos devolubles Y pedidos agrupados
    productos_devolubles = []
    pedidos_agrupados = {}
    
    for pedido in pedidos:
        items = pedido.items.all()
        
        # Guardar info del pedido
        if items.exists() and pedido.id not in pedidos_agrupados:
            pedidos_agrupados[pedido.id] = {
                'pedido_id': pedido.id,
                'fecha_pedido': pedido.fecha_creacion.strftime('%d/%m/%Y'),
                'cantidad_productos': items.count()
            }
        
        for item in items:
            productos_devolubles.append({
                'pedido_id': pedido.id,
                'producto_id': item.producto.id,
                'producto_nombre': item.producto.nombProduc,
                'cantidad': item.cantidad,
                'precio': float(item.precio_unitario),
                'fecha_pedido': pedido.fecha_creacion.strftime('%d/%m/%Y')
            })
    
    # Procesar formulario POST
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        pedido_id = request.POST.get('pedido_id')
        motivo = request.POST.get('motivo')
        foto1 = request.POST.get('foto1', '')
        foto2 = request.POST.get('foto2', '')
        foto3 = request.POST.get('foto3', '')
        
        if not producto_id or not pedido_id or not motivo:
            messages.error(request, 'Por favor completa todos los campos obligatorios')
            return redirect('productos:devoluciones')
        
        try:
            producto = Producto.objects.get(id=producto_id)
            pedido = Pedido.objects.get(id=pedido_id, usuario=request.user, estado='entregado')  # ✅ VERIFICAR ENTREGADO
            
            # ✅ NUEVO: Verificar que no exista devolución previa para este producto en este pedido
            devolucion_existente = Devolucion.objects.filter(
                usuario=request.user,
                producto=producto,
                pedido=pedido
            ).exists()
            
            if devolucion_existente:
                messages.warning(request, 'Ya existe una solicitud de devolución para este producto.')
                return redirect('productos:devoluciones')
            
            # Crear devolución
            devolucion = Devolucion.objects.create(
                usuario=request.user,
                producto=producto,
                pedido=pedido,
                motivo=motivo,
                estado='Pendiente',
                foto1=foto1 if foto1 else None,
                foto2=foto2 if foto2 else None,
                foto3=foto3 if foto3 else None
            )
            
            messages.success(request, f'✅ Solicitud de devolución #{devolucion.id} enviada exitosamente!')
            return redirect('productos:devoluciones')
            
        except Exception as e:
            messages.error(request, f'Error al crear la devolución: {str(e)}')
            return redirect('productos:devoluciones')
    
    # Convertir a JSON para JavaScript
    import json
    productos_json = json.dumps(productos_devolubles)
    
    # Obtener devoluciones del usuario
    mis_devoluciones = Devolucion.objects.filter(
        usuario=request.user
    ).select_related('producto', 'pedido').order_by('-fecha_solicitud')
    
    context = {
        'productos_devolubles': productos_json,
        'pedidos_agrupados': pedidos_agrupados.values(),
        'devoluciones': mis_devoluciones
    }
    
    return render(request, 'productos/devoluciones.html', context)


def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, "productos/detalle.html", {"producto": producto})