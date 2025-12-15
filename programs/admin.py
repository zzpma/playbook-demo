# programs/admin.py
from django.contrib import admin
from .models import Program, Session, Registration

class SessionInline(admin.TabularInline):
    model = Session
    extra = 0

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "reg_deadline", "created_by")
    inlines = [SessionInline]
    readonly_fields = ("public_id",)
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("participant_name", "program", "email", "status", "created_at")
    readonly_fields = ("created_at",)

