from django.conf.urls import url
from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('',views.PostList.as_view(),name='all'),
    path('new/', views.CreatePost.as_view(), name='create'),
    url(r'^by/(?P<username>[-\w]+)/$', views.UserPost.as_view(), name='for_user'),
    # url(r'^by/(?P<username>[-\w]+)/(?P<pk>\d+)/$', views.PostDetail.as_view(), name='single'),
    url(r'^delete/(?P<pk>\d+)/$', views.DeletePost.as_view(), name='delete'),
    url(r'^edit/(?P<pk>\d+)/$', views.EditPost.as_view(), name='edit'),
    url(r'^comment/(?P<pk>\d+)/$', views.CreateComment.as_view(), name='create_comment'),
    url(r'^comment/delete/(?P<pk>\d+)/$', views.DeleteComment.as_view(), name='delete_comment'),
    url(r'^test/(?P<username>[-\w]+)/(?P<pk>\d+)/$', views.post_detail, name='single'),
]
