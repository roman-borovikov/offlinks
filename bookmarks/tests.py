from django.test import TestCase

# Create your tests here.
class PostTestCase(TestCase):
    def test_save(self):
        assertTrue(self.title is not None)
