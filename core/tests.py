from django.test import TestCase
from django.urls import reverse


class BrandingTests(TestCase):
    def test_home_page_uses_truecheck_branding(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TrueCheck')
        self.assertContains(response, 'TRUETRACE SOLUTION')
