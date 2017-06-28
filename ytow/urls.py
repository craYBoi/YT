"""ytow URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from video import views as video_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
	url(r'^capture/', video_views.capture, name='video_capture'),
	url(r'^cms/$', video_views.cms, name='cms'),
    url(r'^cms/(?P<vid_id>[0-9]+)/$', video_views.video, name='video_detail'),
    url(r'^cms/open/$', video_views.open, name='video_open'),
    url(r'^cms2/$', video_views.cms2, name='cms2'),
    url(r'^cms2/(?P<vid_id>[0-9]+)/$', video_views.video2, name='video_detail2'),
    url(r'^api/open$', video_views.ajax_open, name='video_ajax_open'),
    url(r'^api/update$', video_views.ajax_update, name='video_ajax_update'),
    url(r'^api/trim$', video_views.ajax_trim, name='video_ajax_trim'),
    url(r'^api/upload$', video_views.ajax_upload, name='video_ajax_upload'),
    url(r'^api/info$', video_views.ajax_info, name='video_ajax_info'),
]
