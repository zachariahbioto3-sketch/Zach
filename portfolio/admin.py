from django.contrib import admin
from .models import WebsiteTemplate

@admin.register(WebsiteTemplate)
class WebsiteTemplateAdmin(admin.ModelAdmin):
    list_display  = ('title', 'category', 'price', 'is_featured', 'created_at')
    list_filter   = ('category', 'is_featured')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
