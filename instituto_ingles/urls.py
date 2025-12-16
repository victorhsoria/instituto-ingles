from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

handler403 = "instituto_ingles.views.error_403"
urlpatterns = [
    path("admin/", admin.site.urls),

    path(
        "login/",
        auth_views.LoginView.as_view(template_name="login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    # Rutas de la app "alumnos" (home, alumnos, pagos, reportes, etc.)
    path("", include("alumnos.urls")),
]
