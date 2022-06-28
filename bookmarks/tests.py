from django.test import TestCase
from .models import Bookmarks
# Create your tests here.
class PBookmarkTestCase(TestCase):
    def test_save(self):
        self.assertTrue(self.title is not None)
