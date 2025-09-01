from django.contrib.auth.decorators import user_passes_test, login_required

def admin_required(view_func):
    return login_required(user_passes_test(lambda u: u.rol == 'admin', login_url='usuarios:login')(view_func))