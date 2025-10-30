# Imports de biblioteca estándar de Python
import calendar
import json
import random

# Imports de Django core
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import urlsafe_base64_decode

# Imports de terceros
import openpyxl
from openpyxl.utils import get_column_letter

# Imports de la aplicación productos
from productos.forms import CategoriaForm
from productos.models import Calificacion, CarritoItem, Category, Producto

# Imports de la aplicación actual (usuarios)
from .decorators import admin_required
from .forms import EditarPerfilForm, LoginForm, MensajeForm, UsuarioCreationForm
from .models import Mensaje, Pedido, Usuario
from .utils import enviar_email_activacion
from django.core.mail import send_mail
from django.conf import settings


# Create your views here.

def register(request):
    return render(request, 'usuarios/register.html')

def nosotros(request):
    return render(request, 'usuarios/nosotros.html')

def contacto(request):
    return render(request,"usuarios/contacto.html")

def index(request):
    return render(request,"usuarios/index.html")



@admin_required
def dashboard(request):
    # Métricas principales
    total_usuarios = Usuario.objects.count()
    total_productos = Producto.objects.count()
    total_pedidos = Pedido.objects.count()
    total_ventas = Pedido.objects.aggregate(Sum("total"))["total__sum"] or 0

    # Ventas por mes (para tabla/barras)
    ventas_por_mes = (
        Pedido.objects
        .annotate(month=TruncMonth("fecha_creacion"))
        .values("month")
        .annotate(total=Sum("total"))
        .order_by("month")
    )
    ventas_info = []
    for v in ventas_por_mes:
        mes = calendar.month_abbr[v["month"].month]
        ventas_info.append((mes, float(v["total"])))

    # Estado de pedidos
    pedidos_estado = Pedido.objects.values("estado").annotate(cantidad=Count("id"))
    estado_info = [(p["estado"], p["cantidad"]) for p in pedidos_estado]

    # Productos más vendidos
    productos_mas_vendidos = Producto.objects.order_by("-vendidos")[:5]
    prod_info = [(p.nombProduc, p.vendidos) for p in productos_mas_vendidos]

    # Usuarios más frecuentes
    usuarios_frecuentes = (
        Usuario.objects.annotate(num_pedidos=Count("pedido"))
        .order_by("-num_pedidos")[:5]
    )
    usuarios_info = [(u.nombre, u.num_pedidos) for u in usuarios_frecuentes]

    #  Mensajes recientes
    mensajes = Mensaje.objects.order_by("-fecha_envio")[:5]

    context = {
        "total_usuarios": total_usuarios,
        "total_productos": total_productos,
        "total_pedidos": total_pedidos,
        "total_ventas": total_ventas,
        "ventas_info": ventas_info,
        "estado_info": estado_info,
        "prod_info": prod_info,
        "usuarios_info": usuarios_info,
        "mensajes": mensajes,  # 👈 ahora sí estarán disponibles en el template
    }
    return render(request, "usuarios/dashboard.html", context)


@admin_required
def gstUsuarios(request):
    usuarios = Usuario.objects.all().order_by('id')  # opcional: ordenados por id
    
    # Paginación
    paginator = Paginator(usuarios, 10)  # 10 usuarios por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "usuarios/gstUsuarios.html", {
        'page_obj': page_obj,
        'usuarios': page_obj.object_list  # lista de usuarios de la página actual
    })

def loginAdm(request):
    return render(request, "usuarios/loginAdm.html")


def register_view(request):
    if request.method == "POST":
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # ya se guarda como is_active=False
            enviar_email_activacion(user, request)  # enviamos el correo de activación
            return render(request, "usuarios/confirmacion.html")  # mensaje de revisa tu correo
        else:
            print("❌ Errores del formulario:", form.errors)
    else:
        form = UsuarioCreationForm()
    return render(request, "usuarios/register.html", {"form": form})


def login_view(request):
    mensaje = ""
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, username=email, password=password)
            if user is not None and user.rol == "cliente":
                login(request, user)

                # ✅ sincronizar carrito de sesión con BD
                carrito_sesion = request.session.get("carrito", {})
                for key, value in carrito_sesion.items():
                    producto_id = int(key)
                    cantidad = int(value["cantidad"])
                    producto = Producto.objects.get(id=producto_id)

                    item, creado = CarritoItem.objects.get_or_create(
                        usuario=user, producto=producto,
                        defaults={"cantidad": cantidad}
                    )
                    if not creado:
                        item.cantidad += cantidad
                        item.save()

                # ✅ cargar carrito de BD a la sesión
                carrito_db = CarritoItem.objects.filter(usuario=user)
                carrito_dict = {}
                for item in carrito_db:
                    carrito_dict[str(item.producto.id)] = {
                        "cantidad": item.cantidad,
                        "precio": float(item.producto.precio),
                        "nombProduc": item.producto.nombProduc,
                        "imgProduc": item.producto.imgProduc.url,
                    }
                request.session["carrito"] = carrito_dict
                request.session.modified = True

                return redirect('productos:producto')
            else:
                mensaje = "Correo o contraseña incorrectos o no eres cliente"
    else:
        form = LoginForm()

    return render(request, 'usuarios/login.html', {"form": form, "mensaje": mensaje})


def loginAdmin(request):
    mensaje = ""
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, username=email, password=password)
            if user is not None and user.rol == "admin":
                login(request, user)
                return redirect('usuarios:dashboard')
            else:
                mensaje = "Credenciales incorrectas o no eres administrador"
    else:
        form = LoginForm()

    return render(request, 'usuarios/loginAdm.html', {"form": form, "mensaje": mensaje})

def logout_view(request):
    logout(request)
    if "carrito" in request.session:
        del request.session["carrito"]
    return redirect("usuarios:login")

@login_required(login_url='usuarios:login')
def editar_perfil(request):
    user = request.user  # usuario autenticado

    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect('usuarios:editar_perfil')
        else:
            messages.error(request, " Hubo errores en el formulario, revisa los campos.")
    else:
        form = EditarPerfilForm(instance=user)

    return render(request, 'usuarios/editar_perfil.html', {'form': form})




@login_required(login_url='usuarios:login')
def mis_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user)
    return render(request, 'usuarios/mis_pedidos.html', {'pedidos': pedidos})

@admin_required
def cambiar_estado_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    usuario.is_active = not usuario.is_active
    usuario.save()
    return redirect('usuarios:gstUsuarios')  # Cambia si tu ruta tiene otro nombre

@admin_required
def agregar_usuario(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('email')
        telefono = request.POST.get('phone_number')
        rol = request.POST.get('rol')
        password = request.POST.get('password')  # Asegúrate de tener un input para la contraseña

        # Validar si el email ya existe
        if Usuario.objects.filter(email=correo).exists():
            messages.error(request, 'Ya existe un usuario con ese correo.')
            return render(request, 'usuarios/gstUsuarios.html')

        # Crear usuario usando create_user para manejar contraseña
        Usuario.objects.create_user(
            email=correo,
            nombre=nombre,
            phone_number=telefono,
            rol=rol,
            password=password,
            is_active=True
        )

        messages.success(request, 'Usuario agregado correctamente.')
        return redirect('usuarios:gstUsuarios')

    return render(request, 'usuarios/agregar.html')


@admin_required
def informe_calificaciones(request):
    calificaciones = Calificacion.objects.select_related('usuario', 'servicio').all()

    # 🔹 Filtros
    buscar = request.GET.get('buscar')
    estado = request.GET.get('estado')

    if buscar:
        calificaciones = calificaciones.filter(
            Q(usuario__nombre__icontains=buscar) |
            Q(comentario__icontains=buscar)
        )

    if estado == 'aprobado':
        calificaciones = calificaciones.filter(aprobado=True)
    elif estado == 'rechazado':
        calificaciones = calificaciones.filter(aprobado=False)

    # 🔹 Exportar a Excel (todas las calificaciones filtradas)
    if request.GET.get('exportar') == 'excel':
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Calificaciones"

        # Encabezados
        headers = ["Usuario", "Punt. Servicio", "Punt. Productos", "Comentario", "Servicio", "Fecha"]
        for col_num, header in enumerate(headers, 1):
            ws[f"{get_column_letter(col_num)}1"] = header

        # Datos
        for row_num, c in enumerate(calificaciones, 2):
            ws[f"A{row_num}"] = c.usuario.nombre if c.usuario else "Anónimo"
            ws[f"B{row_num}"] = c.puntuacion_servicio
            ws[f"C{row_num}"] = c.puntuacion_productos
            ws[f"D{row_num}"] = c.comentario
            ws[f"E{row_num}"] = c.servicio.tipo if c.servicio else "N/A"
            ws[f"F{row_num}"] = c.fecha_creacion.strftime("%Y-%m-%d %H:%M")

        # Respuesta HTTP
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="calificaciones.xlsx"'
        wb.save(response)
        return response

    # 🔹 Ordenar por fecha y paginar
    calificaciones = calificaciones.order_by('-fecha_creacion')
    paginator = Paginator(calificaciones, 25)  # 25 registros por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'usuarios/informe_calificaciones.html', {
        'page_obj': page_obj,
        'calificaciones': page_obj.object_list
    })

@admin_required
def pedidos_view(request):
    pedidos = Pedido.objects.all().order_by('-fecha_creacion')

    # 🔹 Paginación
    paginator = Paginator(pedidos, 25)  # 25 pedidos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 🔹 Conteos por estado
    pedidos_pendientes = Pedido.objects.filter(estado="pendiente").count()
    pedidos_enviados = Pedido.objects.filter(estado="enviado").count()
    pedidos_entregados = Pedido.objects.filter(estado="entregado").count()

    # 🔹 Total pedidos
    total_pedidos = pedidos.count()

    return render(request, "usuarios/gst_pedidos.html", {
        "page_obj": page_obj,
        "pedidos": page_obj.object_list,
        "pedidos_pendientes": pedidos_pendientes,
        "pedidos_enviados": pedidos_enviados,
        "pedidos_entregados": pedidos_entregados,
        "total_pedidos": total_pedidos,
    })

def productos_mas_vendidos_view(request):
    productos = Producto.objects.annotate(num_pedidos=Count('pedido')).order_by('-num_pedidos')
    return render(request, "usuarios/dashboard.html", {"productos": productos})


def usuarios_frecuentes_view(request):
    usuarios = Usuario.objects.annotate(num_pedidos=Count('pedido')).order_by('-num_pedidos')
    return render(request, "usuarios/dashboard.html", {"usuarios": usuarios})



def contacto(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        correo = request.POST.get("correo")
        asunto = request.POST.get("asunto")
        mensaje = request.POST.get("mensaje")

        Mensaje.objects.create(
            nombre=nombre,
            correo=correo,
            asunto=asunto,
            mensaje=mensaje
        )
        return redirect("usuarios:contacto")

    return render(request, "usuarios/contacto.html")

def aprobar_comentario(request, id):
    calificacion = get_object_or_404(Calificacion, id=id)
    calificacion.aprobado = True
    calificacion.save()
    return redirect('usuarios:informe_calificaciones')

def rechazar_comentario(request,id):
    calificacion = get_object_or_404(Calificacion, id=id)
    calificacion.delete()
    return redirect('usuarios:informe_calificaciones')


def informe_ventas(request):
    pedidos_list = Pedido.objects.all().order_by('-fecha_creacion')

    paginator = Paginator(pedidos_list, 25)  # máximo 25 registros por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    total_ventas = pedidos_list.aggregate(Sum('total'))['total__sum'] or 0
    total_pedidos = pedidos_list.count()

    context = {
        'page_obj': page_obj,   # 👈 pasamos page_obj a la plantilla
        'total_ventas': total_ventas,
        'total_pedidos': total_pedidos,
    }
    return render(request, 'usuarios/ventas.html', context)

User = get_user_model()

def activar_cuenta(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, "usuarios/activado.html")
    else:
        return render(request, "usuarios/activacion_invalida.html")
    
    
def cambiar_estado_pedido(request, pedido_id):
    try:
        data = json.loads(request.body)
        nuevo_estado = data.get('estado')
        
        # Validar estado
        estados_validos = ['pendiente', 'enviado', 'entregado']
        if nuevo_estado not in estados_validos:
            return JsonResponse({'success': False, 'message': 'Estado no válido'})
        
        # Actualizar pedido
        pedido = get_object_or_404(Pedido, id=pedido_id)
        pedido.estado = nuevo_estado
        pedido.save()
        
        return JsonResponse({'success': True, 'message': 'Estado actualizado correctamente'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
    
def editar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == "POST":
        usuario.nombre = request.POST.get("nombre")
        usuario.email = request.POST.get("email")
        usuario.phone_number = request.POST.get("phone_number")
        usuario.rol = request.POST.get("rol")
        usuario.save()

        messages.success(request, "Usuario actualizado correctamente.")
        return redirect("usuarios:gstUsuarios")  # 👈 ajusta al nombre de tu vista/listado

    messages.error(request, "Método no permitido")
    return redirect("usuarios:gstUsuarios")


def enviar_codigo_verificacion(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            
            # Verificar credenciales
            user = authenticate(request, username=email, password=password)
            
            if user is None:
                return JsonResponse({
                    'success': False,
                    'mensaje': 'Credenciales incorrectas'
                })
            
            # Generar código de 6 dígitos
            codigo = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            
            # Guardar código en cache por 10 minutos
            cache_key = f'verification_code_{email}'
            cache.set(cache_key, codigo, 600)  # 600 segundos = 10 minutos
            
            # Enviar email
            asunto = 'Código de verificación - Unidos pensando en su salud'
            mensaje = f'''
Hola {user.nombre or 'Usuario'},

Tu código de verificación es: {codigo}

Este código expirará en 10 minutos.

Si no solicitaste este código, ignora este mensaje.

Saludos,
Equipo de Unidos pensando en su salud
            '''
            
            send_mail(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            return JsonResponse({
                'success': True,
                'mensaje': 'Código enviado exitosamente'
            })
            
        except Exception as e:
            print(f"Error al enviar código: {str(e)}")
            return JsonResponse({
                'success': False,
                'mensaje': f'Error al enviar el código: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'mensaje': 'Método no permitido'})


# Actualizar la vista de login para verificar el código
def login_admin(request):
    if request.method == 'POST':
        codigo_verificacion = request.POST.get('codigo_verificacion')
        email = request.POST.get('email_verified')
        password = request.POST.get('password_verified')
        
        if codigo_verificacion and email:
            # Verificar código
            cache_key = f'verification_code_{email}'
            codigo_guardado = cache.get(cache_key)
            
            if codigo_guardado is None:
                return render(request, 'usuarios/loginAdm.html', {
                    'mensaje': 'El código ha expirado. Por favor, solicita uno nuevo.'
                })
            
            if codigo_verificacion != codigo_guardado:
                return render(request, 'usuarios/loginAdm.html', {
                    'mensaje': 'Código de verificación incorrecto.'
                })
            
            # Código correcto, autenticar usuario
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                # Eliminar código del cache
                cache.delete(cache_key)
                
                # Hacer login
                login(request, user)
                return redirect('nombre_de_tu_vista_admin')
            else:
                return render(request, 'usuarios/loginAdm.html', {
                    'mensaje': 'Error en la autenticación.'
                })
    
    return render(request, 'usuarios/loginAdm.html')