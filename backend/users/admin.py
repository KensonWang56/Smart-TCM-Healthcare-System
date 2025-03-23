from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'create_time', 'last_login_time', 'has_face', 'is_staff')
    list_filter = ('is_staff', 'has_face', 'create_time')
    search_fields = ('username', 'email')
    ordering = ('-create_time',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('个人信息', {'fields': ('avatar', 'has_face', 'face_image')}),
        ('权限', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('时间信息', {'fields': ('create_time', 'last_login_time')}),
        ('其他', {'fields': ('need_change_password',)}),
    )
    readonly_fields = ('create_time', 'last_login_time')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

admin.site.register(User, UserAdmin) 