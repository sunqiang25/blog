# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from django.core.urlresolvers import reverse

class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'Tag'
# Create your models here.
class Article(models.Model):
    STATUS_CHOICES =(
        ('d','Draft'),
        ('p','Published'),
    )
    PROPERTY_CHOICES =(
        ('o','Original'),
        ('r','Reprint'),
    )
    title = models.CharField('title',max_length=100)
    body = models.TextField('body')
    created_time = models.DateTimeField('created_time',auto_now_add=True)
    last_modified_time = models.DateTimeField('last_modified_time',auto_now=True)
    status = models.CharField('status',max_length=1,choices=STATUS_CHOICES)
    property = models.CharField('property',max_length=1,choices=PROPERTY_CHOICES,default='r')
    abstract = models.CharField('abstract',max_length=60,blank=True,null=True,help_text="optional,the first 60 characters if empty")
    views = models.PositiveIntegerField('views',default=0)
    likes = models.PositiveIntegerField('likes',default=0)
    imgurl = models.CharField('imgurl',max_length=255,null=True,blank=True)
    topped = models.BooleanField('topped',default=False)
    category = models.ForeignKey('category',verbose_name='Category',null=True,on_delete=models.SET_NULL) #?
    tags = models.ManyToManyField(Tag,blank=True)
    author = models.ForeignKey(User)

    def increase_views(self):
        self.views+=1
        self.save(update_fields=['views'])

    def increase_likes(self):
        self.likes+=1
        self.save(update_fields=['likes'])

    def __unicode__(self):
        return self.title

    class Meta:
        db_table = 'Article'
        ordering = ['-last_modified_time']

    '''注意到 URL 配置中的 url(r'^post/(?P<pk>[0-9]+)/$', views.detail, name='detail') ，我们设定的 name='detail' 在这里派上了用场。看到这个 reverse 函数，它的第一个参数的值是 'blog:detail'，意思是 blog 应用下的 name=detail 的函数，由于我们在上面通过 app_name = 'blog' 告诉了 Django 这个 URL 模块是属于 blog 应用的，因此 Django 能够顺利地找到 blog 应用下 name 为 detail 的视图函数，于是 reverse 函数会去解析这个视图函数对应的 URL，我们这里 detail 对应的规则就是 post/(?P<pk>[0-9]+)/ 这个正则表达式，而正则表达式部分会被后面传入的参数 pk 替换，所以，如果 Post 的 id（或者 pk，这里 pk 和 id 是等价的） 是 255 的话，那么 get_absolute_url 函数返回的就是 /post/255/ ，这样 Post 自己就生成了自己的 URL'''

    def get_absolute_url(self):
        return reverse('Blog:detail',kwargs={'pk':self.pk})

class Category(models.Model):
    name = models.CharField('category_name',max_length=20)
    created_time = models.DateTimeField('created_time',auto_now_add=True)
    last_modified_time = models.DateTimeField('last_modified_time',auto_now=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'Category'

