import hashlib
from django.conf import settings

def generar_hash_integridad(order_id, amount, currency='COP'):
    """
    Genera el hash SHA256 para validar la integridad de la transacción
    """
    cadena = f"{order_id}{amount}{currency}{settings.BOLD_SECRET_KEY}"
    hash_generado = hashlib.sha256(cadena.encode()).hexdigest()
    return hash_generado