# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,get_object_or_404
from Blog_Module.models import Article
from Blog_Module.models import Category,Tag
import markdown
from django.shortcuts import render,render_to_response,HttpResponse,redirect
from django.http import StreamingHttpResponse,HttpResponseRedirect
from comments.forms import CommentForm
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.views.generic import ListView
from django.db.models import Q
import os
import json
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
import pyecharts,math,requests
from django.contrib.auth.decorators import login_required
from .task import incr_readtimes,incr_likes,data
from PIL import Image,ImageDraw,ImageFont
'''register&Login'''
from django.contrib.auth import logout,authenticate,login
from django.contrib.auth.models import User,Group
from django.core.urlresolvers import reverse

from crypto import encrypt,decrypt             #加密解密
from django.core.mail import EmailMultiAlternatives   #发送邮件
import time,re,datetime
from comments.models import get_avatar_url,User_Avatar
from django.core.cache import cache
from comments.github import get_user_info,get_access_token,get_github_auth
from markdown.extensions.toc import TocExtension
from django.utils.text import slugify

class blog_index(ListView):
    model = Article
    template_name = 'index.html'
    context_object_name = 'articles_list'
    paginate_by = 5
    def get_queryset(self):
        article_list = Article.objects.filter(status='p').order_by('-created_time')
        #for article in article_list:
            #article.body = markdown(article.body,
                                    #extensions=[
                                        #'markdown.extensions.extra',
                                        #'markdown.extensions.codehilite',
                                        #'markdown.extensions.toc',
                                    #])
        return article_list

def blog_detail(request,pk):

    detail = get_object_or_404(Article,pk=pk)
    #Articles_num = len(Article.objects.all())
    id_list = []
    for obj in Article.objects.all():
        id_list.append(int(obj.id))
    id_list_new = sorted(id_list)
    Last_id = id_list_new[-1]
    #detail.increase_views()
    r=incr_readtimes.delay(pk)
    #print r.state,r.get()
    l = incr_likes.delay(pk)
    #print l.state,l.get()
    #detail.increase_likes()
    md = markdown.Markdown(extensions=['markdown.extensions.extra','markdown.extensions.codehilite',TocExtension(slugify=slugify),])
    detail.body = md.convert(detail.body)
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
        'toc':md.toc,
        'comment_list':comment_list
    }

    return render(request,'article_detail.html',context=context)

def archives(request,year,month,day):
    y = year
    m= month.zfill(2) #liang wei, bu zu bu 0
    d = day.zfill(2)
    articles_list = Article.objects.filter(created_time__startswith='%d-%02d-%02d'%(int(y),int(m),int(d))).order_by('-created_time')
    #print articles_list
    num = len(articles_list)
    print num
    return render_to_response('archives_category_tags.html',{'articles_list':articles_list,'num':num})

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
    myfiles = os.path.join(Root_path, 'upload/Love/')
    key = "file_list"
    if cache.has_key(key):
        file_list = cache.get(key)
    else:
        if os.path.isdir(myfiles):
            file_list = []
            for root, dirs, files in os.walk(myfiles,False):
                for f in files:
                    ext = ['.jpg', '.png', '.jpeg']
                    if f.endswith(tuple(ext)):
                        file_list.append(os.path.join(f))
        else:
            file_list =[]
            file_name = myfiles
            file_list.append(file_name)
        cache.set(key,file_list,1*60)
    return render_to_response('Love.html',{'file_list':json.dumps(file_list)})

@login_required
def Resume(request):
    return render_to_response('Resume.html')
@csrf_exempt
def Upload(request):
    Root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    myfiles = os.path.join(Root_path, 'upload/Love/')
    if request.method == "POST":
        if not request.FILES.get('img'):
            return HttpResponse("老婆，上传图片好不啦？")
        else:
            obj = request.FILES.get('img')
            print obj
            f = open(myfiles+obj.name,'wb+')
            for chunk in obj.chunks():
                f.write(chunk)
            f.close()
            im = Image.open(myfiles + obj.name).convert('RGBA')
            img_width, img_height = im.size[0], im.size[1]
            rate = 1.0
            #set the compress rate
            if img_width >=2000 or img_height>=2000:
                rate = 0.3
            elif img_width>=1000 or img_height >=1000:
                rate = 0.5
            elif img_width>=500 or img_height >=500:
                rate = 0.9
            img_width = int(img_width*rate)
            img_height = int(img_height*rate)
            im.thumbnail((img_width,img_height),Image.ANTIALIAS) #create compress pic

            txt = Image.new('RGBA', im.size, (0, 0, 0, 0))
            fnt = ImageFont.truetype("/usr/share/fonts/MSYHL.TTC", 20)
            d = ImageDraw.Draw(txt)
            mark = u"孙强的个人博客"
            d.text((img_width - 150, img_height - 30), mark, font=fnt, fill=(255, 0, 0, 255))
            out = Image.alpha_composite(im, txt)
            print out
            out.save(myfiles + obj.name[:-4] + '.png')
            out.close()
            os.remove(myfiles+obj.name)
            #return HttpResponse('上传完成！')
	    return render_to_response('message.html')
    return render_to_response('upload.html')

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

def zip_download(request, path):
	s = StringIO.StringIO()
	# Root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	# myfiles = os.path.join(Root_path, 'upload/logs/')
	# temp = os.path.join(myfiles, path[1:])
	temp = path + '/'
	dst = path.split('/')[-1][:-9]
	zip_filename = dst + ".zip"
	zf = zipfile.ZipFile(dst + '.zip', "w", zipfile.ZIP_STORED, allowZip64=True)
	for dirname, subdirs, files in os.walk(temp):
		for filename in files:
			absname = os.path.abspath(os.path.join(dirname, filename))
			arcname = absname[len(temp) + 1:]
			zf.write(absname, arcname)
	zf.close()

	def file_iterator(file_name, chunk_size=5120):
		with open(file_name, 'rb') as f:
			while True:
				c = f.read(chunk_size)
				if c:
					yield c
				else:
					break

	resp = StreamingHttpResponse(file_iterator(zip_filename))
	resp['Content-Type'] = 'application/x-zip-compressed'
	# resp = HttpResponse(s.getvalue(), content_type = "application/x-zip-compressed")
	resp['Content-Disposition'] = 'attachment;filename="{0}"'.format(zip_filename)
	return resp

@csrf_exempt
def contact(request):
    if request.method == 'POST':
        print request.POST['contactSubject'],request.POST['contactMessage'],request.POST['contactEmail'].encode('ascii')
        send_mail(request.POST['contactSubject'],'My name is: %s'%request.POST['contactName']+'\n'+'My Mail address is: %s'%request.POST['contactEmail']+'\n'+request.POST['contactMessage'],'530631372@qq.com',['530631372@qq.com'],fail_silently=False)
        send_mail('RE:%s' %request.POST['contactSubject'], 'Thanks for the Message, I will get back to you as ASAP!','530631372@qq.com', [request.POST['contactEmail'].encode('ascii')], fail_silently=False)
        return HttpResponse('OK')

        #return HttpResponseRedirect('/resume/#contact')
    else:
        return render(request,'Resume.html')

def aboutMe(request):
    gauge = pyecharts.Gauge('', background_color='#f5f5f5')
    gauge.add('title', 'Percent', 80.66, scale_range=[0, 100], is_more_utils=True)
    gauge.show_config()
    result = gauge.render_embed()
    data = [("宿迁", 9), ("武汉", 10), ("重庆", 12), ("哈尔滨", 18), ("乌鲁木齐", 10), ("北京", 15),("南京", 13)]
    geo = pyecharts.Geo("中国各城市PM2.5含量示意图", "data from pm2.5", title_color="#000", title_pos="center",
                        background_color='#f5f5f5')
    attr, value = geo.cast(data)
    geo.add("", attr, value, type="effectScatter", is_random=True, effect_scale=5, is_more_utils=True)
    geo.show_config()
    result1 = geo.render_embed()
    attr = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    v1 = [20, 33, 133, 124, 24, 313]
    v2 = [2.6, 12, 31, 241, 324, 134]
    bar = pyecharts.Bar('Bar Sample', background_color='#f5f5f5')
    bar.add("A", attr, v1, mark_line=["average"], mark_point=["min", "max"])
    bar.add("B", attr, v2, mark_line=["average"], mark_point=["min", "max"], is_more_utils=True)
    bar_result = bar.render_embed()
    pie = pyecharts.Pie('', background_color="#f5f5f5")
    pie.add("", attr, v1, is_lable_show=True, lable_text_color="#156ACF", is_more_utils=True)
    pie.show_config()
    pie_result = pie.render_embed()
    liquid = pyecharts.Liquid('', background_color="#000")
    liquid.add("", [0.66, 0.5], ['diamond'], ['#294D99', '#156ACF'], is_more_utils=True)
    liquid.show_config()
    liquid_result = liquid.render_embed()
    l3d = line3d()
    l3d_result = l3d.render_embed()
    name = ['afaaf', 'Tom han', 'ajf oafoa', 'auoj aoudh', 'ad da fa', 'auohdahb da']
    value = [10000, 1132, 414, 1313, 3452, 1413, ]
    wordcloud = pyecharts.WordCloud(width=800, height=400, background_color="#000")
    wordcloud.add("", name, value, word_size_range=[20, 100], rotate_step=50)
    wordcloud.show_config()
    w = wordcloud.render_embed()
    REMOTE_HOST = "https://pyecharts.github.io/assets/js"
    return render_to_response('AboutMe.html',{'result': result, 'result1': result1, 'bar_result': bar_result, 'pie_result': pie_result,'liquid_result': liquid_result,'l3d_result':l3d_result,'host':REMOTE_HOST,'script_list':l3d.get_js_dependencies(),'w':w})
def line3d():
    _data = []
    for t in range(0, 25000):
        _t = t / 1000
        x = (1 + 0.25 * math.cos(75 * _t)) * math.cos(_t)
        y = (1 + 0.25 * math.cos(75 * _t)) * math.sin(_t)
        z = _t + 2.0 * math.sin(75 * _t)
        _data.append([x, y, z])
    range_color = [
        '#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf',
        '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
    line3d = pyecharts.Line3D("3D line plot demo")
    line3d.add("", _data, is_visualmap=True,
               visual_range_color=range_color, visual_range=[0, 30],
               is_grid3D_rotate=True, grid3D_rotate_speed=180)
    return line3d

def get_data(request):
    keyword = request.GET.get('keyword')
    error_Message = ''
    if not keyword:
        error_Message = 'Please input the keyword!'
        return render_to_response('data_from_github.html',{'error_Message':error_Message})
    r =data.delay(keyword)
    #print r.get()
    bar = pyecharts.Bar('编写'+keyword+'最多的语言', background_color='#f5f5f5')
    attr, value = bar.cast(r.get().items())
    #print attr
    #print value
    bar.add(keyword, attr,value, mark_line=["average"], mark_point=["min", "max"],xaxis_rotate=60,xaxis_interval=0)
    bar.show_config()
    bar_data = bar.render_embed()

    return render_to_response('data_from_github.html',{'bar_data':bar_data})

def check_is_login(request):
    """check the user is logined"""
    if request.user.is_authenticated:
        username = request.user.username
        avatar = request.user.get_avatar_url()
        if str(avatar).startswith("http"):
	    avatar = avatar
	else:
	    avatar = '/upload/%s'%(avatar)
        t = datetime.datetime.now().hour
        say_hi = ''
        if 0<= t < 12:
            say_hi = u"早上好"
        elif 12<= t < 18:
            say_hi = u"下午好"
        else:
            say_hi = u"晚上好"
        if request.user.is_active:
            active_state = u'(已激活)'
        else:
            active_state = u'(未激活)'

        returnText = u''' 
            <li class="dropdown"> 
                <a class="dropdown-toggle" data-toggle="dropdown" href="#"> 
                    您好，%s%s <b class="caret"></b> 
                </a> 

                <ul class="dropdown-menu"> 
                    <li><a href="%s">退出</a></li> 
                </ul> 
            </li>''' % (username, active_state, reverse('Blog:user_logout'))  # 用reverse逆向解析user_logout得到网址
        returnText1 = u'''
        <a href="%s">退出</a>
        '''%(reverse('Blog:user_logout'))
        returnText2 = u'''
            <div id="nav-header" class="navbar" >
        <ul class="nav">

       <li class="page_item">
            <img id="imgId" src="%s" style="width:60px;height: 60px;border-radius: 30px;"><span style="color:red">%s,%s</span>
            <ul class="sub-menu">
                <li><a href="#">%s</a></li>
                <li><a href="/admin/">发表文章</a></li>
		      <li><a href='/modify_avatar'>修改头像</a></li>
                <li><a href="%s">退出</a></li>

            </ul>
        </li>
        </ul>
        </div>
        '''% (avatar,say_hi,request.user,active_state, reverse('Blog:user_logout'))
    else:
        # 登录不成功就返回“登录”、“注册”的菜单
        returnText2 = u''' 
            <ul>
            <li style="font-size:10px;color:red"><a href="#" data-toggle="modal" data-target="#LoginModal" >登 录</a></li>&
            <li style="font-size:10px;color:red"><a href="#" data-toggle="modal" data-target="#RegModal" >注 册</a></li>
            </ul>
            '''
    return HttpResponse(returnText2, content_type='application/javascript')


def user_logout(request):
    """logout"""
    logout(request)
    # 记住来源的url，如果没有则设置为首页('/')
    returnPath = request.META.get('HTTP_REFERER', '/')
    # 重定向到原来的页面，相当于刷新
    return HttpResponseRedirect(returnPath)


# 由于用ajax提交，设置不到csrf，就先不进行csrf验证
@csrf_exempt
def user_login(request):
    """login"""
    response_data = {}

    try:
        login_name = request.POST.get('login_name')
        login_pwd = request.POST.get('login_pwd')
        print login_name

        if len(login_name) * len(login_pwd) == 0:
            raise Exception(u"用户名或密码为空")

            # 判断是否正确
        user = authenticate(username=login_name, password=login_pwd)
        print user
        if user is not None:
            login(request, user)  # 登录
        else:
            raise Exception(u"您注册了吗？还是用户名或密码不正确？")

        response_data['success'] = True
        response_data['message'] = 'ok'

    except Exception as e:
        response_data['success'] = False
        response_data['message'] = e.message
    finally:
        # 返回json数据
        return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def user_reg(request):
    response_data = {}
    reg_email = ''

    try:
        reg_uname = request.POST.get('reg_uname')
        reg_email = request.POST.get('reg_email')
        reg_pwd = request.POST.get('reg_pwd')

        if len(reg_email) * len(reg_pwd) == 0:
            raise Exception(u"邮箱或密码为空")

        # 匹配邮箱格式
        pattern = re.compile(r'^^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$')
        match = pattern.match(reg_email)
        if not match:
            raise Exception(u"邮箱格式不正确")

        # 验证密码长度
        if len(reg_pwd) < 6:
            raise Exception(u"密码不能少于6位")

        uname = User.objects.filter(username=reg_uname)
        if len(uname) > 0:
            raise Exception("用户名已存在")
        # 判断用户是否存在
        user = User.objects.filter(email=reg_email)
        if len(user) > 0:
            raise Exception(u"该邮箱已经被注册")

        # 创建新用户
        user = User(username=reg_uname, email=reg_email)
        user.set_password(reg_pwd)  # 这样才会对密码加密处理
        user.is_active = False
        user.is_staff = True
        user.save()
        group = Group.objects.get(name="Guest")
        user.groups.add(group)

        response_data['success'] = True
        response_data['message'] = u'注册成功，并发送激活邮件到您的邮箱。'
    except Exception as e:
        response_data['success'] = False
        response_data['message'] = e.message
    finally:
        if response_data['success']:
            try:
                # 发送激活邮件
                # 不想用uuid模块生成唯一ID保存到数据库中，也不想用django-registration
                # 安全级别要求不高，所以简单写个加密解密的方法来处理
                active_code = get_active_code(reg_email)
                send_active_email(reg_email, active_code)
            except Exception as e:
                response_data['message'] = u'注册成功，激活邮件发送失败。请稍后重试 ' + e.message

            # 注册成功，登录用户
            user = authenticate(username=reg_uname, password=reg_pwd)
            if user is not None:
                login(request, user)

        return HttpResponse(json.dumps(response_data), content_type="application/json")


def get_active_code(email):
    """get active code by email and current date"""
    key = 9
    encry_str = '%s|%s' % (email, time.strftime('%Y-%m-%d', time.localtime(time.time())))
    active_code = encrypt(key, encry_str)
    return active_code


def send_active_email(email, active_code):
    """send the active email"""
    url = 'http://39.106.189.163%s' % (reverse('Blog:user_active', args=(active_code,)))

    subject = u'[孙强的个人博客]激活您的帐号'
    message = u'''
        <h2>孙强的个人博客(<a href="http://39.106.189.163/" target=_blank>39.106.189.163</a>)<h2><br />
        <p>欢迎注册，请点击下面链接进行激活操作(3天后过期)：<a href="%s" target=_balnk>立即注册</a></p>
        ''' % (url)

    send_to = [email]
    fail_silently = True  # 发送异常不报错
    msg = EmailMultiAlternatives(subject=subject, body=message,from_email='530631372@qq.com',to=send_to)
    msg.attach_alternative(message, "text/html")
    msg.send(fail_silently)


def user_active(request, active_code):
    """user active from the code"""
    # 加错误处理，避免出错。出错认为激活链接失效
    # 解密激活链接
    key = 9
    data = {}
    try:
        decrypt_str = decrypt(key, active_code)
        decrypt_data = decrypt_str.split('|')
        email = decrypt_data[0]  # 邮箱
        create_date = time.strptime(decrypt_data[1], "%Y-%m-%d")  # 激活链接创建日期
        create_date = time.mktime(create_date)  # struct_time 转成浮点型的时间戳

        day = int((time.time() - create_date) / (24 * 60 * 60))  # 得到日期差
        if day > 3:
            raise Exception(u'激活链接已过期')

        # 激活
        user = User.objects.filter(email=email)
        if len(user) == 0:
            raise Exception(u'激活链接无效，请重新激活！')
        else:
            user = User.objects.get(email=email)

        if user.is_active:
            raise Exception(u'该帐号已激活过了')
        else:
            user.is_active = True
            user.save()

        data['goto_page'] = True
        data['message'] = u'激活成功，欢迎访问孙强的博客！'
    except IndexError as e:
        data['goto_page'] = False
        data['message'] = u'激活链接无效'
    except Exception as e:
        data['goto_page'] = False
        data['message'] = e
    finally:
        # 激活成功就跳转到首页(message页面有自动跳转功能)
        data['goto_url'] = '/'
        data['goto_time'] = 3000
        return render_to_response('test_Message.html', data)
@csrf_exempt	
def modify_avatar(request):
    error = ''
    if request.method == 'POST':
        if not request.FILES.get('img'):
            error = u'Please upload the pic'
        else:
            user_1 = User.objects.get(username=request.user)
            user_avatar = User_Avatar(user=user_1,avatar=request.FILES.get('img'))
            user_avatar.save()
            return HttpResponseRedirect('/')
    return render_to_response('Modify_avatar.html',{'error':error})	


def third_login(request):
    #callback_url = get_github_auth()
    code = request.GET['code']
    access_token = get_access_token(code)
    try:
        gid, email, nick, avatar = get_user_info(access_token)
    except Exception as e:
        return HttpResponse(e.message)
    pwd = "1qaz@WSX_!"
    try:
        uname = ''
        get_name = User.objects.filter(username=nick)

        if len(get_name)>0:
            try_user = authenticate(username=get_name[0],password=pwd)
            print try_user,'2'
            if try_user is not None:
		avatar_user = User.objects.get(username=get_name[0])
		user_avatar = User_Avatar(user=avatar_user,avatar=avatar)
		user_avatar.save()
                login(request,try_user)
                return redirect('/')
            else:
                uname = '%s_%s'%(nick,gid)
        else:
            uname = nick
        #user = User(username=uname, email=email)
        user = User(username=uname,email=email)
        user.set_password(pwd)  # 这样才会对密码加密处理
        user.is_active = True
        user.is_staff = True
        group = Group.objects.get(name='Guest')
        user.save()
        user.groups.add(group)
        user_1 = User.objects.get(username=uname)
        user_avatar = User_Avatar(user=user_1, avatar=avatar)
        user_avatar.save()
        github_user = authenticate(username=uname,password=pwd)
        print github_user,'3'
        if github_user is not None:
            login(request, github_user)
    except Exception as e:
        return HttpResponse(e.message)

    return redirect('/')
