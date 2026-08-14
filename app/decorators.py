from django.shortcuts import redirect
from functools import wraps

def seller_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if (
            request.user.is_authenticated
            and request.user.user_type == 2
            and request.user.status
        ):
            return view_func(request, *args, **kwargs)
        return redirect('seller_pending')
    return wrapper
