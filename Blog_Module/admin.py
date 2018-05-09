# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from Blog_Module.models import Article
from Blog_Module.models import Category,Tag

# Register your models here.
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title','body','status','abstract','author']
    list_per_page = 5
    search_fileds = ('title','author',)
   # date_hierarchy = 'go_time'

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fileds = ('name',)

class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fileds = ('name',)

class MyModelAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super(MyModelAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(author=request.user)

admin.site.register(Article,ArticleAdmin)
admin.site.register(Category,CategoryAdmin)
admin.site.register(Tag,TagAdmin)
