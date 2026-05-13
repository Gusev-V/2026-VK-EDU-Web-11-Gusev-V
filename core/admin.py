from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_user_email', 'nickname', 'created_at']
    list_filter = ['created_at']
    search_fields = ['nickname', 'user__username', 'user__email']
    raw_id_fields = ['user']
    readonly_fields = ['created_at']

    @admin.display(description='Email', ordering='user__email')
    def get_user_email(self, obj):
        return obj.user.email

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')