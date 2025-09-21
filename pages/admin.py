from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import AdminProfile, Visit, Download, AnalyticsSummary

# Register your models here.

class AdminProfileInline(admin.StackedInline):
    model = AdminProfile
    can_delete = False
    verbose_name_plural = 'Admin Profile'

class CustomUserAdmin(UserAdmin):
    inlines = (AdminProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')

# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_admin', 'created_at')
    list_filter = ('is_admin', 'created_at')
    search_fields = ('user__username', 'user__email')

@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'page_url', 'user', 'timestamp')
    list_filter = ('timestamp', 'user')
    search_fields = ('ip_address', 'page_url', 'user__username')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'

@admin.register(Download)
class DownloadAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'ip_address', 'user', 'download_count', 'timestamp')
    list_filter = ('timestamp', 'user')
    search_fields = ('file_name', 'ip_address', 'user__username')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'

@admin.register(AnalyticsSummary)
class AnalyticsSummaryAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_visits', 'unique_visitors', 'total_downloads', 'unique_downloads')
    list_filter = ('date',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date'
