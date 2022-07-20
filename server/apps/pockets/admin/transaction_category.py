from django.contrib import admin

from ..models import TransactionCategory


@admin.register(TransactionCategory)
class TransactionCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    # list_filter = ('category_type',)
    search_fields = ('name', 'user')
