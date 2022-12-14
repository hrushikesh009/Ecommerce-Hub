from urllib import response
from django.test import TestCase

class UrlTestCase(TestCase):
    def test_url(self):
        response = self.client.get('http://127.0.0.1:8000/store/')
        self.assertEqual(response.status_code,200)

