from django.urls import path
from . import views

urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("procesar/", views.procesar_pago, name="procesar_pago"),
    path("pagos/success/", views.pago_exitoso, name="pago_exitoso"),
    path("pagos/failure/", views.pago_fallido, name="pago_fallido"),
    path('webhook/', views.webhook_mercadopago, name='webhook'),
]