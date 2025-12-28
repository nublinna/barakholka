from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from django.contrib.auth import login
from django.shortcuts import redirect
from user.forms import SignUpForm


def signup_view(request: HttpRequest):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("ads:ads_list")
    else:
        form = SignUpForm()

    return render(request, 'signup.html', context={'form': form})