from django.contrib import admin
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Admin configuration for Book model"""

    list_display = ['title', 'author', 'genre', 'price', 'stock', 'published_year', 'created_at']
    list_filter = ['genre', 'published_year', 'created_at', 'stock']
    search_fields = ['title', 'author', 'isbn', 'genre', 'description']
    list_editable = ['price', 'stock']
    list_per_page = 25
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'author', 'isbn', 'published_year', 'genre')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'stock')
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ['id', 'created_at', 'updated_at']

    def get_queryset(self, request):
        """Optimize queryset for admin"""
        queryset = super().get_queryset(request)
        return queryset.select_related()

    def has_delete_permission(self, request, obj=None):
        """Allow deletion for superusers only"""
        return request.user.is_superuser
