from django.contrib import admin
from .models import Category, Book, Summary


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', )
    list_display_links = ('name',)
    ordering = ('name',)


class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'pri', 'time', 'rgst', 'status')
    list_display_links = ('id', 'name',)
    ordering = ('id', 'status',)


class SummaryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'updt', 'rgst')
    list_display_links = ('id', 'title',)
    ordering = ('id',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Summary, SummaryAdmin)
