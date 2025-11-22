from django.db import transaction
from .models import Lote

@transaction.atomic
def descontar_stock(producto, cantidad_solicitada):
    lotes = Lote.objects.filter(producto=producto).order_by('fecha_caducidad')

    cantidad_restante = cantidad_solicitada
    lote_usado = None

    for lote in lotes:
        if cantidad_restante <= 0:
            break

        if lote_usado is None:
            lote_usado = lote.codigo_lote  # ← SE GUARDA EL PRIMER LOTE USADO

        if lote.cantidad > cantidad_restante:
            lote.cantidad -= cantidad_restante
            lote.save()
            cantidad_restante = 0
        else:
            cantidad_restante -= lote.cantidad
            lote.delete()

    if cantidad_restante > 0:
        raise ValueError("No hay suficiente stock en los lotes para completar la venta.")

    return lote_usado
