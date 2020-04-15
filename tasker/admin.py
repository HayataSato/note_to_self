from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import Category, Task, Summary


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', )
    list_display_links = ('name',)
    ordering = ('name',)


class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'pri', 'time', 'rgst', 'status')
    list_display_links = ('id', 'name',)
    ordering = ('id', 'status',)


class SummaryAdmin(MarkdownxModelAdmin):
    list_display = ('id', 'title', 'updt', 'rgst')
    list_display_links = ('id', 'title',)
    ordering = ('id',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Summary, SummaryAdmin)
