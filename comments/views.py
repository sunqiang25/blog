# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,render_to_response,get_object_or_404,redirect
from comments.models import Comment
from comments.forms import CommentForm
from Blog_Module.models import Article,Category,Tag
from django.core.mail import send_mail,EmailMultiAlternatives
from django.contrib.auth.models import User
import re
from Blog_Module.task import comment_send_email

def post_comment(request,post_pk):
    #get the article need to comments
    post = get_object_or_404(Article,pk=post_pk)

    if request.method == 'POST':
        form = CommentForm(request.POST) #gou zao form, shi li hua
        if form.is_valid():

            comment = form.save(commit=False) #jin jin sheng cheng biao dan, zan shi hai bu bao cun dao shu ju ku
            #jiang ping lun yu wen zhang guan lian qi lai
	    comment.name = request.user
            comment.post = post
            comment.save() #bao cun shu ju dao shu ju ku
	    comment_send_email.delay(comment.text,post.title,post_pk,request.user.email)
            return redirect(post)  #chong ding xiang
        else:
            comment_list = post.comment_set.all()
            context = {
                'post':post,
                'form':form,
                'comment_list':comment_list,
                }
            return render_to_response('article_detail.html',context=context)
