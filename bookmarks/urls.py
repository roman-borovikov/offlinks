from django.urls import path, re_path, include
from bookmarks import views


urlpatterns = [
    re_path('^$', views.bookmarks, name='bookmarks'),
    re_path('^add_bookmark/$', views.add_bookmark, name='add_bookmark'),
    re_path('^del_bookmark/(?P<title_slug>[\w\-]+)/$', views.del_bookmark, name='del_bookmark'),
    re_path('^search/$', views.search_bookmark, name='search_bookmark'),
    re_path('^import/$', views.import_bookmarks, name='import_bookmarks'),
    re_path('^export/$', views.export_bookmarks, name='export_bookmarks'),
    re_path('^(?P<title_slug>[\w\-]+)/$', views.view_bookmark, name='view_bookmark'),
]