"""frontend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path

from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^walletinfo/$', views.walletinfo, name='walletinfo'),
    url(r'^identity/$', views.identity, name='identity'),
    url(r'^portfolio/$', views.portfolio, name='portfolio'),
    url(r'^portfolio/artwork/(?P<artid>.*)$', views.artwork, name='artwork'),
    url(r'^trading/(?P<function>(transfer|trade|consummate))$', views.trading, name='trading'),
    url(r'^exchange/$', views.exchange, name='exchange'),
    url(r'^trending/$', views.trending, name='trending'),
    url(r'^browse/(?P<txid>.*)$', views.browse, name='browse'),
    url(r'^register/$', views.register, name='register'),
    url(r'^console/$', views.console, name='console'),
    url(r'^explorer/(?P<functionality>(chaininfo|block|transaction|address))/?(?P<id>.*)?$', views.explorer, name='explorer'),
    url(r'^chunk/(?P<chunkid_hex>.*?)$', views.chunk, name='chunk'),
    url(r'^$', views.index, name='index'),
]
