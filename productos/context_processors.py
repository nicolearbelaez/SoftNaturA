from .models import Category

def carrito_y_categorias(request):
    carrito = request.session.get("carrito", {})
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

    return {
        "carrito_items": items,
        "carrito_subtotal": round(subtotal, 2),
        "carrito_iva": round(iva, 2),
        "carrito_total": round(total, 2),
        "carrito_cantidad": total_cantidad,
        "categorias": categorias,   # 👈 ahora siempre disponible
    }
