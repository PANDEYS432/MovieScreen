from django.shortcuts import redirect

def admin_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_staff or request.user.is_superuser:            
            return view_func(request, *args, *kwargs)
        else:
            return redirect('history')
    return wrapper_func