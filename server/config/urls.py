from django.contrib import admin
from django.contrib.auth import views as auth
from django.urls import path
from core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", auth.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth.LogoutView.as_view(), name="logout"),
    path("senha/", auth.PasswordChangeView.as_view(template_name="registration/password_change_form.html"), name="password_change"),
    path("senha/alterada/", auth.PasswordChangeDoneView.as_view(template_name="registration/password_change_done.html"), name="password_change_done"),
    path("health/", views.health, name="health"),
    path("", views.dashboard, name="dashboard"),
    path("relatorios/", views.reports, name="reports"),
    path("relatorios/chamados.csv", views.export, name="export"),
    path("equipe/", views.team, name="team"),
    path("equipe/nova/", views.team_edit, name="team_create"),
    path("equipe/<int:pk>/editar/", views.team_edit, name="team_edit"),
    path("<slug:module>/", views.listing, name="list"),
    path("<slug:module>/novo/", views.edit, name="create"),
    path("<slug:module>/<int:pk>/", views.detail, name="detail"),
    path("<slug:module>/<int:pk>/editar/", views.edit, name="edit"),
    path("<slug:module>/<int:pk>/status/", views.progress, name="progress"),
    path("<slug:module>/<int:pk>/comentar/", views.comment, name="comment"),
]
