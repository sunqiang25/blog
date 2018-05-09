from django.conf.urls import url,include
from Blog_Module import views
from Blog import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

path_end = r'(?P<path>[\w\d_ -/.]*)$'
app_name = 'Blog'
urlpatterns = [
    url(r'^$',views.blog_index.as_view()),
    url(r'^article/(?P<pk>[0-9]+)/?$',views.blog_detail,name='detail'),
    url(r'^archive/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/(?P<day>[0-9]{1,2})/?$', views.archives),
    url(r'^category/(?P<pk>[0-9]+)/?$', views.category),
    url(r'^tag/(?P<tag_name>.+)/?$', views.tag),
    url(r'^search/?$', views.search,name='search'),
    url(r'^love/?$', views.Love,name='Love'),
    url(r'^resume/?$', views.Resume,name='Resume'),
    #url(r'^sendmail/(?P<emailto>[\w.%+-]+@[A-Za-z0-9.-]+[A-Za-z]{2,4})/', views.sendMail,name='SendMail'),
    url(r'^contact/?$', views.contact,name='Contact'),
    url(r'^about/?$',views.aboutMe,name='AboutMe'),
    url(r'upload/?$',views.Upload,name="Upload"),
    url(r'get_data/?$',views.get_data,name='get_data'),
    url(r'^check_is_login$', views.check_is_login, name='check_is_login'),
    url(r'^user_logout$', views.user_logout, name='user_logout'),
    url(r'^user_login$', views.user_login, name='user_login'),
    url(r'^user_reg$',views.user_reg,name='user_reg'),
    url(r'^user_active/([a-zA-Z]+)$',views.user_active,name='user_active'),
    url(r'^accounts/login/$',auth_views.login,name='login'),
    url(r'^modify_avatar/?$',views.modify_avatar,name='modify_avatar'),
    url(r'^login/callback\?*',views.third_login,name="callback"),
]+ static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)
