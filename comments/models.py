# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from types import MethodType #类动态绑定方法
import os
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import User


class Comment(models.Model):
    name = models.ForeignKey(User,related_name='user_comments',null=True,blank=True,on_delete=models.SET_NULL,default=None)
    email = models.EmailField(max_length=255,blank=True)
    url = models.URLField(blank=True)
    text = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)

    post = models.ForeignKey('Blog_Module.Article')

    def __unicode__(self):
        return self.text[:20]
    class Meta:
        ordering = ['-created_time']
        db_table = 'Comment'

AVATAR_ROOT = 'avatar'
AVATAR_DEFAULT = os.path.join(AVATAR_ROOT, 'Logo.jpeg')


class User_Avatar(models.Model):
    """user avatar"""
    user = models.ForeignKey(User)
    avatar = models.ImageField(upload_to=AVATAR_ROOT)


# 动态绑定头像相关的方法
def get_avatar_url(self):
    try:
        avatar = User_Avatar.objects.filter(user=self.id)
        avatar = avatar[len(avatar)-1]
        return avatar.avatar
    except Exception as e:
        return AVATAR_DEFAULT


# 动态绑定方法
User.get_avatar_url = MethodType(get_avatar_url, None, User)


