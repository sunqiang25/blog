# -*- coding: utf-8 -*-
from Blog_Module.models import Article,Tag,Category
from comments.models import Comment
from django import template
from django.db.models.aggregates import Count


register = template.Library()

@register.simple_tag
def get_recent_articles(num=5):
    return Article.objects.all().order_by('-created_time')[:num] #get zui xin chuang jian de wen zhang de qian 3 ge

@register.simple_tag
def archives():
    return Article.objects.datetimes('created_time','day',order='DESC').annotate(num=Count('created_time'))

 #get create time and jingque dao yue fen, jiang xu pai lie
'''
@register.simple_tag
def get_categories():
    return Category.objects.all()
'''
@register.simple_tag
def get_tags():
    return Tag.objects.all()

@register.simple_tag
def get_comments():
    return Comment.objects.all()[:8]

@register.simple_tag
def get_categories():
    return Category.objects.annotate(num_posts=Count('article')).filter(num_posts__gt=0) #使用 filter 方法把 num_posts 的值小于 1 的分类过滤掉。因为 num_posts 的值小于 1 表示该分类下没有文章

@register.simple_tag
def get_maxViews():
    return Article.objects.all().order_by('-views')[:6]


