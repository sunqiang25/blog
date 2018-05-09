# -*- coding: utf-8 -*-
from django.db.models import F
from .models import Article
from Blog import celery_app
import requests,json,re
from django.core.mail import send_mail,EmailMultiAlternatives
from django.contrib.auth.models import User


@celery_app.task
def incr_readtimes(article_id):
    return Article.objects.filter(id=article_id).update(views=F('views')+1)

@celery_app.task
def incr_likes(article_id):
    return Article.objects.filter(id=article_id).update(likes=F('likes')+2)

@celery_app.task
def data(keyword):
    url = 'https://api.github.com/search/repositories?q=%s&sort=forks&order=desc&per_page=1000'%(keyword)
    All_data = requests.get(url)
    hjson = json.loads(All_data.text)
    data = hjson['items']
    language=[]
    for item in data:
        language.append(item['language'])
    set_lauguage = set(language)
    #language_list=[]
    #num_list =[]
    list={}
    for i in set_lauguage:
        list[i] = language.count(i)
        #language_list.append(i)
        #num_list.append(language.count(i))

    return list
@celery_app.task
def comment_send_email(text,post_title,post_pk,user_comment_email):
    user_reply = re.findall('@(.*?)\s', text)
    if user_reply:
        for users in user_reply:
            user_reply_email = User.objects.get(username=users).email
            subject = "Your comment has a new reply on article '%s'" % (post_title)
            message = u'''<h2>孙强的个人博客(<a href="http://39.106.189.163/" target=_blank>39.106.189.163</a>)<h2><br /><p>Your comment has a new reply on article '%s', you can click <a href="http://39.106.189.163/article/%s" target=_balnk>Here</a> to view,Thanks</p>''' % (post_title, post_pk)

            send_to = [user_reply_email]
            fail_silently = True  # 发送异常不报错
            msg = EmailMultiAlternatives(subject=subject, body=message, from_email='530631372@qq.com', to=send_to)
            msg.attach_alternative(message, "text/html")
            msg.send(fail_silently)

    else:
        subject = "Thanks for your comment on SunQiang's blog"
        message = '''<p>Thanks for your comment on the article <a href="http://39.106.189.163/article/%s">%s</a></p>''' % (post_pk, post_title)
        send_to = [user_comment_email]
        fail_silently = True
        msg = EmailMultiAlternatives(subject=subject, body=message, from_email='530631372@qq.com', to=send_to)
        msg.attach_alternative(message, "text/html")
        msg.send(fail_silently)
