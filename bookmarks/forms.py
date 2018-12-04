from django import forms
from bookmarks.models import Bookmarks
from django.contrib.auth.models import User

class AddBookmarkForm(forms.ModelForm):
    url = forms.URLField(max_length=200, help_text="Please enter the URL of the page.")
    title = forms.CharField(widget=forms.HiddenInput(), required=False)
    added_by = forms.ModelChoiceField(widget=forms.HiddenInput(), queryset=User.objects.all())
    content = forms.CharField(widget=forms.HiddenInput(), required=False)
    slugtitle = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        # Provide an association between the ModelForm and a model
        model = Bookmarks

        fields = ('url','title','added_by','content', 'slugtitle')

class ImportBookmarksForm(forms.Form):
    import_file = forms.FileField()

    