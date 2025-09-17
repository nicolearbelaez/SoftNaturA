from django.shortcuts import render, redirect
from .models import Usuario , Mensaje
from productos.models import Producto, Calificacion
from .forms import LoginForm, UsuarioCreationForm
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import EditarPerfilForm
from usuarios.decorators import admin_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
import csv
from .models import Pedido
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
import calendar
from django.contrib import messages
from .forms import MensajeForm


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

    # Ventas por mes (para gráfico de barras)
    ventas_por_mes = (
        Pedido.objects
        .annotate(month=TruncMonth("fecha_creacion"))
        .values("month")
        .annotate(total=Sum("total"))
        .order_by("month")
    )

    labels = []
    data = []
    for v in ventas_por_mes:
        labels.append(calendar.month_abbr[v["month"].month])  # Ene, Feb, Mar...
        data.append(float(v["total"]))

    # Estado de pedidos (para gráfico circular)
    pedidos_estado = Pedido.objects.values("estado").annotate(cantidad=Count("id"))
    estados = [p["estado"] for p in pedidos_estado]
    cantidades = [p["cantidad"] for p in pedidos_estado]

    context = {
        "total_usuarios": total_usuarios,
        "total_productos": total_productos,
        "total_pedidos": total_pedidos,
        "total_ventas": total_ventas,
        "labels": labels,
        "data": data,
        "estado_labels": estados,
        "estado_data": cantidades,
        "ventas": Pedido.objects.all().order_by("-fecha_creacion")[:10],  # últimas 10
    }
    return render(request, "usuarios/dashboard.html", context)



@admin_required
def gstUsuarios(request):
    usuarios = Usuario.objects.all()
    return render(request,"usuarios/gstUsuarios.html", {'usuarios': usuarios})

def loginAdm(request):
    return render(request, "usuarios/loginAdm.html")


def register_view(request):
    if request.method == "POST":
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('usuarios:login')  
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

            user = authenticate(request, username=email, password=password)  # validación Django
            if user is not None and user.rol == "cliente":
                login(request, user)  # crea sesión
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
    return redirect("productos:producto")

@login_required(login_url='usuarios:login')
def editar_perfil(request):
    user = request.user
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Perfil actualizado correctamente.")
            return redirect('usuarios:editar_perfil')  # Redirige para mostrar el mensaje en la misma página
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
        correo = request.POST.get('correo')
        telefono = request.POST.get('numTelefono')
        rol = request.POST.get('rol')

        Usuario.objects.create(
            nombre=nombre,
            email=correo,
            numTelefono=telefono,
            rol=rol,
            activo=True
        )
        return redirect('usuarios:gstUsuarios')

@admin_required
def informe_calificaciones(request):
    calificaciones = Calificacion.objects.select_related('usuario', 'servicio').all()

    tipo = request.GET.get('tipo')
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')

    if tipo:
        calificaciones = calificaciones.filter(servicio__tipo=tipo)

    if desde:
        calificaciones = calificaciones.filter(fecha_creacion__gte=desde)

    if hasta:
        calificaciones = calificaciones.filter(fecha_creacion__lte=hasta)

    # Exportar a Excel
    if request.GET.get('exportar') == 'excel':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="calificaciones.csv"'

        writer = csv.writer(response)
        writer.writerow(['Usuario', 'Puntuación', 'Comentario', 'Tipo de Servicio', 'Fecha'])

        for c in calificaciones:
            writer.writerow([
                c.usuario.username if c.usuario else 'Anónimo',
                f"{c.puntuacion_servicio} / {c.puntuacion_productos}",
                c.comentario,
                c.fecha_creacion.strftime('%Y-%m-%d %H:%M')
            ])

        return response

    return render(request, 'usuarios/informe_calificaciones.html', {
        'calificaciones': calificaciones
    })

def estadisticas_ventas(request):
    # Total de ventas
    total_ventas = Pedido.objects.count()

    # Ingresos totales
    ingresos_totales = Pedido.objects.aggregate(Sum("total"))["total__sum"] or 0

    # Productos más vendidos (top 5)
    productos_mas_vendidos = (
        Pedido.objects.values("producto__nombre")
        .annotate(cantidad=Count("producto"))
        .order_by("-cantidad")[:5]
    )

    context = {
        "total_ventas": total_ventas,
        "ingresos_totales": ingresos_totales,
        "productos_mas_vendidos": productos_mas_vendidos,
    }
    return render(request, "usuarios/dashboard.html", context)


def ventas_view(request):
    ventas = Pedido.objects.all().order_by('-fecha')
    return render(request, "usuarios/ventas.html", {"ventas": ventas})

def pedidos_view(request):
    pedidos = Pedido.objects.all().order_by('-fecha_creacion')
    return render(request, "usuarios/gst_pedidos.html", {"pedidos": pedidos})

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
    return redirect('productos:informe_calificaciones')

def rechazar_comentario(request,id):
    calificacion = get_object_or_404(Calificacion, id=id)
    calificacion.delete()
    return redirect('productos:informe_calificaciones')