from django.shortcuts import redirect

def customer_required(view_func):
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("login")

        if request.user.role != "customer":
            return redirect("worker_dashboard")

        return view_func(request, *args, **kwargs)

    return wrapper


def worker_required(view_func):
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("login")

        if request.user.role != "worker":
            return redirect("customer_dashboard")

        return view_func(request, *args, **kwargs)

    return wrapper