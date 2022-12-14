from django.contrib.auth.models import Group
from django.http import HttpResponse
from django.shortcuts import redirect

def unauthenticated_user(view_func):
    def wrapper_func(request,*args,**kwargs):
        if request.user.is_authenticated:
            return redirect('admin-home-view')
        else:
            return view_func(request,*args,**kwargs)
    return wrapper_func

def allowed_users(allowed_roles=[]):
    def allowed(view_func):
        def wrapper_func(request,*args,**kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
                print(group)
            if group in allowed_roles or request.user.is_superuser or request.user.is_staff:
                return view_func(request,*args,**kwargs)
            else:
                return HttpResponse("You are not Authorized to view this Page Please Login with a Admin User" )
        return wrapper_func
    return allowed