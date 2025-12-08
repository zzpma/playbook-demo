from django.shortcuts import render, redirect
from django.http import HttpResponse
from allauth.account.forms import LoginForm 
from django.contrib.auth import logout


def login_view(request):
    logout(request)  # for demo-purposes only

    form = LoginForm(data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            # Perform login
            form.login(request)

            # Redirect if HTMX
            if request.htmx:
                response = HttpResponse(status=204)  # No content
                response["HX-Redirect"] = "/dashboard/"
                return response

            return redirect("/dashboard/")

        # FORM INVALID
        if request.htmx:
            # Return ONLY the form partial
            return render(request, "accounts/login_form_fields.html", {"form": form})

    # GET request or failed non-HTMX POST
    return render(request, "accounts/login.html", {"form": form})


def register_view(request):
    return render(request, "accounts/register.html")
