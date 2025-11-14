# pagos/views.py ESTO ES PARA CQUE SALGA EL COSTO DELL ENVIO DEL DOMICILIO 
import hashlib
import time
import json
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from .models import Transaccion
from usuarios.models import Pedido, Direccion, PedidoItem
from productos.models import Producto

import hashlib
import time
from django.shortcuts import render, redirect
from django.conf import settings
from usuarios.models import Pedido, PedidoItem
from django.db import transaction
from .models import Transaccion
from productos.models import Producto


def checkout(request):
    """Vista del checkout con botón Bold y cálculo de envío"""
    carrito = request.session.get("carrito", {})
    
    if not carrito:
        return redirect("productos:producto")
    
    productos = []
    subtotal = 0

    for item in carrito.values():
        imagen = item.get('imgProduc', '')
        nombre = item.get('nombProduc', 'Sin nombre')
        cantidad = int(item.get('cantidad', 0))
        precio = float(item.get('precio', 0))
        precio_producto = precio * cantidad
        subtotal += precio_producto

        productos.append({
            'imagen': imagen,
            'nombre': nombre,
            'cantidad': cantidad,
            'precio': precio,
            'subtotal': precio_producto
        })

    # CARGAR DIRECCIÓN Y CALCULAR ENVÍO
    direccion_guardada = None
    costo_envio = 0
    modo_edicion = False
    
    if request.user.is_authenticated:
        try:
            direccion_guardada = Direccion.objects.get(usuario=request.user, es_principal=True)
            modo_edicion = request.GET.get('editar', 'false') == 'true'
            
            ciudad = direccion_guardada.ciudad.lower().strip()
            
            # Ibagué: $8,000
            if 'ibague' in ciudad or 'ibagué' in ciudad:
                costo_envio = 8000
            
            # Tolima Regional: $12,000
            elif any(c in ciudad for c in ['espinal', 'melgar', 'honda', 'mariquita', 
                                           'chaparral', 'líbano', 'libano', 'flandes', 
                                           'guamo', 'saldaña', 'saldana', 'purificacion',
                                           'purificación', 'cajamarca', 'armero', 'venadillo']):
                costo_envio = 12000
            
            # Otras ciudades: no se hace envío
            else:
                costo_envio = 0
                
        except Direccion.DoesNotExist:
            pass

    # Calcular IVA y total
    iva = subtotal * 0.19
    total_sin_envio = subtotal + iva
    total_final = total_sin_envio + costo_envio

    pedido = None
    order_id = None

    if request.user.is_authenticated:
        with transaction.atomic():
            timestamp = int(time.time())
            order_id = f"ORD-{timestamp}"

            # Crear el pedido
            pedido = Pedido.objects.create(
                usuario=request.user,
                order_id=order_id,
                total=total_final,
                estado="pendiente",
                pago=True
            )

            print(f"✅ Pedido creado: #{pedido.id} - Total: ${total_final}")

            # Crear los items del pedido
            for producto_id, item in carrito.items():
                try:
                    producto_obj = Producto.objects.get(id=int(producto_id))
                    PedidoItem.objects.create(
                        pedido=pedido,
                        producto=producto_obj,
                        cantidad=int(item.get('cantidad', 0)),
                        precio_unitario=float(item.get('precio', 0))
                    )
                    print(f"🧾 Item agregado: {producto_obj.nombProduc} x{item.get('cantidad')}")
                except Producto.DoesNotExist:
                    print(f"❌ Producto {producto_id} no encontrado")
                    continue

            # Crear transacción
            Transaccion.objects.create(
                order_id=order_id,
                usuario=request.user,
                pedido=pedido,
                monto=total_final,
                estado='pendiente'
            )

    else:
        timestamp = int(time.time())
        order_id = f"ORD-{timestamp}"

    # Hash de integridad para Bold
    amount = int(total_final)
    currency = "COP"
    cadena = f"{order_id}{amount}{currency}{settings.BOLD_SECRET_KEY}"
    integrity_hash = hashlib.sha256(cadena.encode()).hexdigest()

    # URL de redirección
    redirection_url = request.build_absolute_uri('/pagos/respuesta/')

    context = {
        'productos': productos,
        'subtotal': round(subtotal, 2),
        'iva': round(iva, 2),
        'costo_envio': round(costo_envio, 2),
        'total_sin_envio': round(total_sin_envio, 2),
        'total_final': round(total_final, 2),
        'order_id': order_id,
        'amount': amount,
        'currency': currency,
        'integrity_hash': integrity_hash,
        'redirection_url': redirection_url,
        'bold_api_key': settings.BOLD_API_KEY,
        'direccion_guardada': direccion_guardada,
        'modo_edicion': modo_edicion,
    }

    return render(request, 'pagos/checkout.html', context)


def payment_response(request):
    """Recibe respuesta de Bold y actualiza el pedido"""
    order_id = request.GET.get('bold-order-id')
    tx_status = request.GET.get('bold-tx-status')
    
    if not order_id:
        return redirect('productos:producto')
    
    productos_ids = []  # ✅ Lista para guardar los IDs de productos
    
    try:
        transaccion = Transaccion.objects.get(order_id=order_id)
        
        if tx_status == 'approved':
            transaccion.estado = 'approved'

            if transaccion.pedido:
                pedido = transaccion.pedido
                pedido.estado = 'pagado'
                pedido.pago = True
                pedido.save()

                # 🔻 Restar stock de productos comprados
                for item in PedidoItem.objects.filter(pedido=pedido):
                    producto = item.producto
                    productos_ids.append(producto.id)  # ✅ Guardar ID del producto
                    producto.stock -= item.cantidad
                    if producto.stock < 0:
                        producto.stock = 0
                    producto.save()
                    print(f"🟢 Stock actualizado: {producto.nombProduc} → {producto.stock}")

            # Vaciar carrito
            request.session['carrito'] = {}
            request.session.modified = True

        elif tx_status == 'rejected':
            transaccion.estado = 'rejected'
            if transaccion.pedido:
                transaccion.pedido.pago = False
                transaccion.pedido.save()

        else:
            transaccion.estado = 'pending'
        
        transaccion.save()
        
    except Transaccion.DoesNotExist:
        print("⚠️ Transacción no encontrada:", order_id)
    
    # ✅ Pasar el primer producto para calificar (o todos si prefieres)
    context = {
        'order_id': order_id,
        'tx_status': tx_status,
        'producto_id': productos_ids[0] if productos_ids else None,  # ✅ Primer producto
        'productos_ids': productos_ids,  # ✅ Todos los productos (opcional)
    }
    
    return render(request, 'pagos/payment_response.html', context)
 


def webhook_bold(request):
    """Webhook para recibir notificaciones de Bold"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            
            order_id = data.get('order_id')
            status = data.get('status')
            
            if order_id:
                try:
                    transaccion = Transaccion.objects.get(order_id=order_id)
                    transaccion.estado = status
                    transaccion.save()
                    
                    if status == 'approved' and transaccion.pedido:
                        transaccion.pedido.estado = 'pagado'
                        transaccion.pedido.save()
                        
                except Transaccion.DoesNotExist:
                    print(f"Transacción no encontrada: {order_id}")
            
            print("Webhook Bold recibido:", data)
            return HttpResponse(status=200)
            
        except json.JSONDecodeError:
            return HttpResponse("Invalid JSON", status=400)
    else:
        return HttpResponse("Método no permitido", status=405)