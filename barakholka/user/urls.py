from django.urls import path
from django.contrib.auth import views as auth_views
from user.views import signup_view


app_name = "user"

urlpatterns = [
    path("signup/", signup_view, name="signup"),

    path(
        "login/",
        auth_views.LoginView.as_view(template_name="login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="user:login"),
        name="logout",
    )
]