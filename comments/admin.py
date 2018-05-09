# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from comments.models import Comment,User_Avatar

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id','name','text')
    list_per_page = 10
@admin.register(User_Avatar)
class Avatar(admin.ModelAdmin):
    list_display = ('user','avatar')

admin.site.site_header = "SunQiang's Blog"
admin.site.site_title = 'SunQiang Blog Background'
# Register your models here.
