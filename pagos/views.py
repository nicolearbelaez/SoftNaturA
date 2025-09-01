from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import mercadopago
import json

# Coloca tu Access Token aquí
ACCESS_TOKEN = "TU_ACCESS_TOKEN_DE_MERCADOPAGO"

def checkout(request):
    # Página con botón para iniciar pago
    return render(request, "pagos/checkout_api.html")

def procesar_pago(request):
    sdk = mercadopago.SDK(ACCESS_TOKEN)

    preference_data = {
        "items": [
            {
                "title": "Producto ejemplo",
                "quantity": 1,
                "unit_price": 100.00,
            }
        ],
        "back_urls": {
            "success": request.build_absolute_uri('/pagos/success/'),
            "failure": request.build_absolute_uri('/pagos/failure/'),
        },
        "auto_return": "approved",
        "notification_url": request.build_absolute_uri('/webhook/'),
    }

    preference_response = sdk.preference().create(preference_data)
    preference = preference_response["response"]

    return redirect(preference["init_point"])

def pago_exitoso(request):
    return render(request, "pagos/success.html")

def pago_fallido(request):
    return render(request, "pagos/failure.html")

def webhook_mercadopago(request):
    if request.method == "POST":
        # Recibir y procesar la notificación del webhook
        data = json.loads(request.body)

        # Aquí procesas la información (por ejemplo guardar estado en BD)
        print("Webhook recibido:", data)

        return HttpResponse(status=200)
    else:
        return HttpResponse("Método no permitido", status=405)