from django.contrib import admin
from .models import Activity, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'color', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'priority', 'status', 'start_date')
    list_filter = ('category', 'priority', 'status', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    date_hierarchy = 'start_date'
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'user', 'category')
        }),
        ('Scheduling', {
            'fields': ('start_date', 'end_date', 'duration_minutes')
        }),
        ('Status', {
            'fields': ('priority', 'status', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )