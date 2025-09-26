from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Group

def group_required(group_names):
    """
    Decorator que verifica se o usuário pertence a um ou mais grupos.
    Exemplo de uso: @group_required(['Diretor', 'Mediador'])
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                if request.user.is_superuser or request.user.groups.filter(name__in=group_names).exists():
                    return view_func(request, *args, **kwargs)

            raise PermissionDenied
        return wrapper
    return decorator