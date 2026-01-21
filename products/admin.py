from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import Category, Product, ProductImage
from .forms import CategoryForm


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('colored_name', 'image_preview', 'is_active', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    list_display_links = ('colored_name',)
    list_filter = ('is_active', 'created_at')
    list_per_page = 20
    search_fields = ('name', 'description')
    date_hierarchy = 'created_at'
    empty_value_display = '-empty-'
    fieldsets = (
        ('Required', {
            'fields': ('name', 'slug', 'image', 'is_active')
        }),
        (
            'Information', {
                'fields': ('description', 'color_code'),
                'classes': ('collapse',),
            }
        ),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    form = CategoryForm
    actions = ['make_active', 'make_inactive']

    @admin.display(description='Name', ordering='name')
    def colored_name(self, obj):
        return format_html(
            '<span style="color: {};">{}</span>',
            obj.color_code,
            obj.name
        )
    
    @admin.display(description='Image Preview')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return format_html('<span style="color: #888888;">No Image</span>')

    @admin.action(description='Mark selected categories as active')
    def make_active(self, request, queryset):
        updated_count = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated_count} category(ies) were successfully marked as active.'
        )

    @admin.action(description='Mark selected categories as inactive')
    def make_inactive(self, request, queryset):
        updated_count = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated_count} category(ies) were successfully marked as inactive.'
        )


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category__name', 'get_price', 'is_active', 'created_at')
    list_filter = ('is_active', 'category__name', 'created_at')
    list_display_links = ('name', 'category__name')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    date_hierarchy = 'created_at'
    list_per_page = 20
    ordering = ('name',)
    empty_value_display = '-empty-'
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ProductImageInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'sale')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def category__name(self, obj):
        if obj.category:
            url = reverse('admin:products_category_change', args=[obj.category.id])
            return format_html('<a href="{}">{}</a>', url, obj.category.name)
        return '-'
    
    @admin.display(description='Price')
    def get_price(self, obj):
        return format_html(
            '<span style="text-decoration: line-through; color: #999;">${}</span><br><strong style="color: #e74c3c;">${}</strong>', 
            obj.get_price(), 
            obj.get_sale()
        )
