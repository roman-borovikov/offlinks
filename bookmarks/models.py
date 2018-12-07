from django.db import models
from django.contrib.auth.models import User
#from django.template.defaultfilters import slugify
from pytils.translit import slugify

# Create your models here.

class Bookmarks(models.Model):
    added_by = models.ForeignKey(User, on_delete=models.PROTECT)
    url = models.URLField(blank=False)
    title = models.CharField(max_length=200)
    slugtitle = models.SlugField(unique=True)
    content = models.TextField()
  

    def save(self, *args, **kwargs):
        self.slugtitle = slugify(self.added_by.username + " " + self.title)
        super(Bookmarks, self).save(*args, **kwargs)

    def __str__(self): # For Python 2, use __unicode__ too
        return self.title

class Bookmarks_data(models.Model):
    key = models.ForeignKey(Bookmarks, on_delete=models.CASCADE)
    path = models.CharField(max_length=256, default="#")
    data = models.TextField()

    def __str__(self): # For Python 2, use __unicode__ too
        return self.path