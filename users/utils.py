from functools import wraps
from django.http import HttpResponseForbidden


def role_required(role_name):
    """Decorator to require a user to be in a given group/role.

    Usage:
        @role_required('Support Agent')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return HttpResponseForbidden('Authentication required')
            if user.groups.filter(name=role_name).exists() or (role_name == 'Admin' and user.is_staff):
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden('Permission denied')
        return _wrapped
    return decorator
