from .models import Mascota


def mascotas_usuario(request):
    """
    Context processor para incluir las mascotas del usuario en todas las vistas.
    """
    context = {
        'mascotas_usuario': [],
    }
    
    if request.user.is_authenticated:
        mascotas = Mascota.objects.filter(tutor=request.user, activa=True).order_by('nombre')
        # Pasar los objetos completos para tener acceso a todos los campos, incluyendo foto
        context['mascotas_usuario'] = list(mascotas)
    
    return context

