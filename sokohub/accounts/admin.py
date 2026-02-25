from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, SokohubCard

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'phone', 'location', 'is_staff', 'date_joined')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'phone')
    readonly_fields = ('date_joined', 'last_login')

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone', 'location')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone', 'location', 'email')
        }),
    )

@admin.register(SokohubCard)
class SokohubCardAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'phone', 'status', 'is_active', 'created_at')
    list_filter = ('status', 'is_active')
    search_fields = ('user__username', 'email', 'phone')
    actions = ['approve_cards']

    def approve_cards(self, request, queryset):
        queryset.update(status='approved', is_active=True)
        self.message_user(request, "Selected cards have been approved and activated.")
    approve_cards.short_description = "Approve and Activate selected cards"