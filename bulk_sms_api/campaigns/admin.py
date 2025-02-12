from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.utils.html import format_html
from .models import CustomUser, Company, Group, Contact, Campaign

class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Additional info', {'fields': ('role', 'company')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role', 'company'),
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role', 'approve_link', 'reject_link')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

    def approve_link(self, obj):
        if not obj.is_active:
            return format_html('<a href="{}">Approuver</a>', reverse('approve_registration', args=[obj.id]))
        return 'Approuvé'
    approve_link.short_description = 'Approuver'

    def reject_link(self, obj):
        if not obj.is_active:
            return format_html('<a href="{}">Rejeter</a>', reverse('reject_registration', args=[obj.id]))
        return 'Rejeté'
    reject_link.short_description = 'Rejeter'

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Company)
admin.site.register(Group)
admin.site.register(Contact)
admin.site.register(Campaign)