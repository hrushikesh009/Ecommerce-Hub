import logging
from django.http import HttpResponse
from django.shortcuts import redirect

logger = logging.getLogger('django')


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        try:
            if request.user.is_authenticated:
                return redirect('custom_admin:admin-home-view')
            else:
                return view_func(request, *args, **kwargs)
        except Exception as e:
            logger.error(e)
    return wrapper_func


def allowed_users(allowed_roles=[]):
    def allowed(view_func):
        def wrapper_func(request, *args, **kwargs):
            try:
                group = None
                if request.user.groups.exists():
                    group = request.user.groups.all()[0].name
                if group in allowed_roles or request.user.is_superuser or request.user.is_staff:
                    return view_func(request, *args, **kwargs)
                else:
                    return HttpResponse("You are not Authorized to view this Page Please Login with a Admin User<br><a href='/admin/logout/'>Logout</a>")
            except Exception as e:
                logger.error(e)
        return wrapper_func
    return allowed
