# pagos/urls.py
from django.urls import path
from . import views

app_name = 'pagos'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('respuesta/', views.payment_response, name='payment_response'),
]