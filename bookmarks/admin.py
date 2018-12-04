from django.contrib import admin

# Register your models here.
from bookmarks.models import Bookmarks, Bookmarks_data

admin.site.register(Bookmarks)
admin.site.register(Bookmarks_data)