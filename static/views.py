# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render,get_object_or_404
from Blog_Module.models import Article
from Blog_Module.models import Category,Tag
from markdown import markdown
from django.shortcuts import render,render_to_response,HttpResponse
from comments.forms import CommentForm
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.views.generic import ListView
from django.db.models import Q
import os
import json
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
import pyecharts

class blog_index(ListView):
    model = Article
    template_name = 'index.html'
    context_object_name = 'articles_list'
    paginate_by = 5

# Create your views here.
'''
def blog_index(request):
    articles_list = Article.objects.all().order_by('-created_time')
    p = Paginator(articles_list,2)
    page = request.GET.get('page')
    try:
        article = p.page(page)
    except PageNotAnInteger:
        article=p.page(1)
    except EmptyPage:
        article = p.page(p.num_pages)


    return render_to_response('index.html',locals())
'''
def blog_detail(request,pk):

    detail = get_object_or_404(Article,pk=pk)
    #Articles_num = len(Article.objects.all())
    id_list = []
    for obj in Article.objects.all():
        id_list.append(int(obj.id))
    id_list_new = sorted(id_list)
    Last_id = id_list_new[-1]
    detail.increase_views()
    detail.body = markdown(detail.body,
                                    extensions=[
                                        'markdown.extensions.extra',
                                        'markdown.extensions.codehilite',
                                        'markdown.extensions.toc',
                                    ])
    form = CommentForm()
    comment_list = detail.comment_set.all()
    if int(pk) == id_list_new[0]:
        pre_detail = get_object_or_404(Article,pk=pk)
        nex_detail = get_object_or_404(Article,pk=id_list_new[1])
    elif int(pk) == id_list_new[-1]:
        pre_detail = get_object_or_404(Article,pk=id_list_new[-2])
        nex_detail = get_object_or_404(Article,pk=pk)
    else:
        pre_detail = get_object_or_404(Article,pk=id_list_new[id_list_new.index(int(pk))-1])
        nex_detail = get_object_or_404(Article,pk=id_list_new[id_list_new.index(int(pk))+1])
    context = {
        'detail':detail,
        'pre_detail':pre_detail,
        'nex_detail':nex_detail,
        'form':form,
        'Last_id':Last_id,
        'comment_list':comment_list
    }

    return render(request,'article_detail.html',context=context)

def archives(request,year,month,day):
    y = year
    m= month.zfill(2) #liang wei, bu zu bu 0
    d = day.zfill(2)
    articles_list = Article.objects.filter(created_time__startswith='%d-%02d-%02d'%(int(y),int(m),int(d))).order_by('-created_time')
    print articles_list
    return render_to_response('archives_category_tags.html',{'articles_list':articles_list})

def category(request,pk):
    cate = get_object_or_404(Category,pk=pk)
    articles_list = Article.objects.filter(category=cate).order_by('-created_time')
    return render_to_response('archives_category_tags.html', {'articles_list': articles_list})
def tag(request,tag_name):
    tag_id = Tag.objects.get(name=tag_name)
    error_Message = ''
    articles_list = Article.objects.filter(tags=tag_id).order_by('-created_time')
    if len(articles_list) == 0:
        error_Message = 'No article under this tag!'
        return render_to_response('archives_category_tags.html', {'error_Message': error_Message})

    return render_to_response('archives_category_tags.html',{'articles_list': articles_list})

def search(request):
    q = request.GET.get('q')
    error_Message = ''
    if not q:
        error_Message = 'Please input the key!'
        return render_to_response('archives_category_tags.html',{'error_Message':error_Message})
    articles_list = Article.objects.filter(Q(title__icontains=q)|Q(body__icontains=q))
    return render_to_response('archives_category_tags.html',locals())

def Love(request):
    Root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    myfiles = os.path.join(Root_path, 'upload/')
    if os.path.isdir(myfiles):
        file_list = []
        for root, dirs, files in os.walk(myfiles,False):
            for f in files:
                file_list.append(os.path.join(f))
    else:
        file_list =[]
        file_name = myfiles
        file_list.append(file_name)
    return render_to_response('Love1.html',{'file_list':json.dumps(file_list)})


def Resume(request):
    return render_to_response('Resume.html')

def file_download(request):
    # do something...
   
    #BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    BASE_DIR = STATICFILES_DIRS
    the_file_name= BASE_DIR+"/"+request.GET['url']
    def file_iterator(file_name, chunk_size=5120):
        with open(file_name,'rb') as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break
    filename=request.GET['url']
    DownloadName=filename.split("/")[-1]
    response = StreamingHttpResponse(file_iterator(filename))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(DownloadName)

    return response
@csrf_exempt
def contact(request):
    if request.method == 'POST':
        print request.POST['contactSubject'],request.POST['contactMessage'],request.POST['contactEmail'].encode('ascii')
        send_mail(request.POST['contactSubject'],'My name is %s'%request.POST['contactName']+'\n'+'My Mail address is %s'%request.POST['contactEmail']+'\n'+request.POST['contactMessage'],'530631372@qq.com',['530631372@qq.com'],fail_silently=False)
        send_mail('RE:%s' %request.POST['contactSubject'], 'Thanks for the Message, I will get back to you as ASAP!','530631372@qq.com', [request.POST['contactEmail'].encode('ascii')], fail_silently=False)
        return HttpResponse('OK')

        #return HttpResponseRedirect('/resume/#contact')
    else:
        return render(request,'Resume.html')

def aboutMe(request):
    gauge = pyecharts.Gauge('',background_color='#f5f5f5')
    gauge.add('title','Percent', 80.66,scale_range=[0,100],is_more_utils=True)
    gauge.show_config()
    result = gauge.render_embed()
    data = [("海门", 9), ("鄂尔多斯", 10), ("招远", 12), ("舟山", 18), ("齐齐哈尔", 10), ("盐城", 15)]
    geo = pyecharts.Geo("全国主要城市空气质量", "data from pm2.5", title_color="#000", title_pos="center",
               background_color='#f5f5f5')
    attr, value = geo.cast(data)
    geo.add("", attr, value, type="effectScatter", is_random=True, effect_scale=5,is_more_utils=True)
    geo.show_config()
    result1 = geo.render_embed()
    attr = ["Jan","Feb","Mar","Apr","May","Jun"]
    v1 = [20,33,133,124,24,313]
    v2 = [2.6,12,31,241,324,134]
    bar = pyecharts.Bar('Bar Sample',background_color='#f5f5f5')
    bar.add("A",attr,v1, mark_line=["average"],mark_point=["min","max"])
    bar.add("B",attr,v2,mark_line=["average"],mark_point=["min","max"],is_more_utils=True)
    bar_result = bar.render_embed()
    pie = pyecharts.Pie('',background_color="#f5f5f5")
    pie.add("",attr,v1,is_lable_show=True,lable_text_color="#156ACF",is_more_utils=True)
    pie.show_config()
    pie_result = pie.render_embed()
    liquid = pyecharts.Liquid('',background_color="#000")
    liquid.add("",[0.66,0.5],['diamond'],['#294D99','#156ACF'],is_more_utils=True)
    liquid.show_config()
    liquid_result = liquid.render_embed()
    return render_to_response('AboutMe.html',{'result':result,'result1':result1,'bar_result':bar_result,'pie_result':pie_result,'liquid_result':liquid_result})
