from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, AuditEvent

@admin.register(User)
class TeamAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Gestão TI", {"fields": ("role",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Gestão TI", {"fields": ("role", "first_name", "last_name", "email")}),)
    list_display = ("username", "email", "role", "is_active")
    def has_module_permission(self, request): return request.user.is_superuser
    def has_view_permission(self, request, obj=None): return request.user.is_superuser
    def has_add_permission(self, request): return request.user.is_superuser
    def has_change_permission(self, request, obj=None): return request.user.is_superuser
    def has_delete_permission(self, request, obj=None): return False

@admin.register(AuditEvent)
class AuditAdmin(admin.ModelAdmin):
    list_display = ("created_at", "actor", "action", "model", "object_id", "summary")
    list_filter = ("action", "model")
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False
    def has_view_permission(self, request, obj=None): return request.user.is_superuser

admin.site.site_header = "GESTÃO TI · Administração"
admin.site.site_title = "Gestão TI"
admin.site.index_title = "Equipe e auditoria"
