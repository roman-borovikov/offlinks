from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from bookmarks.models import Bookmarks
from bookmarks.forms import AddBookmarkForm
from bookmarks.forms import ImportBookmarksForm
from urllib.request import urlopen
import lxml.html
import re
from django.db import IntegrityError
from django.contrib.auth.models import User
from bookmarks.models import Bookmarks, Bookmarks_data
from django.shortcuts import redirect
from django.core.paginator import Paginator
from django.core.paginator import InvalidPage
from urllib.parse import urlsplit, urlunsplit, urljoin
from pytils.translit import slugify
import os
from django.conf import settings
from pathlib import Path
import glob

def index(request):
    return redirect('/bookmarks/')

def bookmarks(request):
    try:
        page_num = request.GET["page"]
    except:
        page_num = 1
    bookmarks_pages = Paginator(Bookmarks.objects.filter(added_by__username=request.user).order_by('title'), 7, orphans=1)
    try:
        bookmarks_list = bookmarks_pages.page(page_num)
    except InvalidPage:
        bookmarks_list = bookmarks_pages.page(1)

    context_dict = {'bookmarks': bookmarks_list, 'home': 'active'}
    return render(request, 'bookmarks.html', context=context_dict)

def view_bookmark(request, title_slug):
    content_item = ""
    try:
        content_item = Bookmarks.objects.get(slugtitle=title_slug).content
    except Bookmarks.DoesNotExist:    
        content_item = "Sorry, not found or not exist"
    return HttpResponse(content_item)

def search_bookmark(request):
    search_value = request.GET.get('value')
    search_list = Bookmarks.objects.filter(added_by__username = request.user, title__contains = search_value).order_by('title')
    context_dict = {'search_list': search_list, 'search_value': search_value, 'home': 'active'}
    return render(request, 'search.html', context=context_dict)

def export_bookmarks(request):
    bookmarks_list = Bookmarks.objects.filter(added_by__username=request.user)
    content_item = '<!DOCTYPE NETSCAPE-Bookmark-file-1>'
    content_item +=' <META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">'
    content_item +='<TITLE>Bookmarks</TITLE>'
    content_item +='<H1>Bookmarks</H1>'
    content_item +='<DL>'

    for i in bookmarks_list:
        content_item +='<DT><a href="'+i.url+'">'+i.title+'</a>'
    content_item +='</DL>'
    
    return HttpResponse(content_item)

def import_bookmarks(request):
    # A HTTP POST?
    if request.method == 'POST':
        form = ImportBookmarksForm(request.POST, request.FILES)
        # Have we been provided with a valid form?
        if form.is_valid():
            f = request.FILES['import_file']
            t = lxml.html.parse(f)
            links = t.xpath('//a')
            for l in links:
                bookmark_object = Bookmarks()
                bookmark_object.url = l.get('href')
                bookmark_object.title = l.text
                if bookmark_object.title == "":
                    bookmark_object.title = "TITLE NOT FOUND FOR " + bookmark_object.url
                bookmark_object.added_by = request.user
                bookmark_object.content = download_links(bookmark_object.url, slugify(bookmark_object.added_by.username + " " + bookmark_object.title))
                try:
                    bookmark_object.save()                 
                except IntegrityError:
                    continue
                # Get extra files like CSS

            return redirect('/bookmarks/')
        else:
            print(form.errors)
    # This is GET
    else:     
        form = ImportBookmarksForm()
    return render(request, 'import_bookmarks.html', {'form': form, 'import': 'active'} )

def get_content(url):
# get content of the page
    content = ""
    try:
        c = urlopen(url).read()
        content = c.decode('utf-8')
    except:
        content = "Could not upload content from "+ url
    return content    

def get_title(url):
# parse title of the page
    title = ""
    try:
        t = lxml.html.parse(urlopen(url))
        title = t.find("//title").text
    except:
        title = "Could not parse TITLE from " + url
    return title

def download_links(url, slug_title):
# download CSS files, replace links, and return new content of the page
    try:
        t = lxml.html.parse(urlopen(url))
    except:
        return "Cannot open " + url
    css_list = t.xpath('//link[@type="text/css"]/@href')
    key = slug_title
    folder_path = Path(settings.STATIC_DIR)
    cont_out = get_content(url)
    for i in css_list:
        full_url = urljoin(url, i)
        i_norm = re.sub(r"[/]","-",urlsplit(i).path)
        i_norm = re.sub(r"\.\.","-",i_norm)
        try:
            data = urlopen(full_url).read()
        except:
            mess = "Not Found CSS file:" + full_url
            data = mess.encode('utf-8')    
        web_path = "view/" + slug_title + "_" + i_norm
        file_path = Path(web_path)
        file_content = data 
        try:
            f = open( folder_path / file_path, 'wb')
            f.write(file_content)
            f.close            
        except:
            return "Cannot open " + web_path + " in " + url
        cont_out = cont_out.replace(i,"/static/"+web_path)
    return cont_out

def add_bookmark(request):
    try:
        user = User.objects.get(username=request.user)
    except:
        return render(request, 'err_message.html', {'err_message': "Please log in or register!", 'home': 'active'})

    form = AddBookmarkForm(request.POST or None, initial={"added_by": user})
    # A HTTP POST?
    if request.method == 'POST':
        # Have we been provided with a valid form?
        if form.is_valid():
            newbookmark = form.save(commit=False)
            newbookmark.title = get_title(newbookmark.url)
            newbookmark.slugtitle = slugify(user.username + " " + newbookmark.title)
            newbookmark.content = download_links(newbookmark.url, newbookmark.slugtitle)
            try:
                form.save()
            except IntegrityError:
                return render(request, 'err_message.html', {'err_message': "The bookmark with the title exists!"})
            
            return redirect('/bookmarks/search/?value=' + newbookmark.title)
        else:
            print(form.errors)
#    # This is GET
#    else:
        
    return render(request, 'add_bookmark.html', {'form': form, 'home': 'active'})

def del_bookmark(request, title_slug):
    Bookmarks.objects.filter(slugtitle=title_slug).delete()
    # Delete files
    web_path =  "/view/" + title_slug + "*"
    files = glob.glob(settings.STATIC_DIR + web_path)
    for f in files:
        os.remove(f)
    return redirect('/bookmarks/')