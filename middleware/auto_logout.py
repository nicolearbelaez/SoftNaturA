from django.utils import timezone
from datetime import timedelta
from django.shortcuts import redirect

class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Excluir static y media
        if (request.path.startswith("/static/") or request.path.startswith("/media/") or request.path.startswith("/admin/")):
            return self.get_response(request)

        # Usuario no autenticado → continuar normal
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        if request.user.is_staff:
            return self.get_response(request)

        now = timezone.now()
        last_activity = request.session.get("last_activity")

        max_inactive = 259200  # 60 segundos

        if last_activity:
            last_activity = timezone.datetime.fromisoformat(last_activity)
            diff = (now - last_activity).total_seconds()

            print(f"Segundos sin actividad REAL: {diff}")

            if diff > max_inactive:
                from django.contrib.auth import logout
                logout(request)
                
                # 🔥 IMPORTANTE: ENVIAR MARCADOR DE INACTIVIDAD
                return redirect("/usuarios/login/?inactividad=1")

        # Actualizar timestamp
        request.session["last_activity"] = now.isoformat()

        print("Actualizando actividad:", now)

        return self.get_response(request)
