from django.test import TestCase
from django.urls import reverse
from django.contrib.staticfiles import finders
from accounts.models import User
from stories.models import Story, Chapter
from shorts.models import ShortStory


class BrandPresentationTests(TestCase):
    def setUp(self):
        self.reader = User.objects.create_user('+255711234567', 'Reader')
        self.staff = User.objects.create_user('+255712234567', 'Staff')
        self.staff.is_staff = True
        self.staff.save(update_fields=['is_staff'])
        self.story = Story.objects.create(title='Hadithi', description='Test', is_published=True)
        self.chapter = Chapter.objects.create(story=self.story, order=1, title='Mwanzo', content='Paragraph one.\n\nParagraph two.')
        self.short = ShortStory.objects.create(title='Fupi', content='Short reading content.', published=True)

    def assert_brand_head(self, response):
        self.assertEqual(response.status_code, 200)
        for path in ['js/theme.js', 'js/qissa.js', 'css/brand.css', 'css/utilities.css', 'favicon.svg']:
            self.assertContains(response, '/static/' + path)
            self.assertIsNotNone(finders.find(path))
        body = response.content.decode()
        self.assertLess(body.index('js/theme.js'), body.index('<body'))
        self.assertNotIn('cdn.tailwindcss.com', body)
        for font in ['Cormorant', 'DM+Sans', 'Literata']:
            self.assertIn(font, body)
        self.assertNotIn('branding/qissa-logo.png', body)  # No invented or broken artwork references.

    def test_public_auth_pricing_and_listing_pages_share_brand_assets(self):
        for name in ['home', 'login', 'register', 'premium', 'stories_list', 'short_list']:
            with self.subTest(page=name):
                self.assert_brand_head(self.client.get(reverse(name)))

    def test_both_readers_share_font_controls_and_keep_navigation(self):
        self.client.force_login(self.reader)
        for name, args in [('chapter_reader', [self.chapter.pk]), ('short_detail', [self.short.slug])]:
            with self.subTest(page=name):
                response = self.client.get(reverse(name, args=args))
                self.assert_brand_head(response)
                self.assertContains(response, 'id="reading-content"')
                self.assertContains(response, 'data-reader-size="-1"')
                self.assertContains(response, 'data-reader-size="1"')
                self.assertContains(response, 'Mipangilio ya kusoma')
        response = self.client.get(reverse('chapter_reader', args=[self.chapter.pk]))
        self.assertContains(response, 'Paragraph one.')
        self.assertContains(response, reverse('chapter_reader', args=[self.chapter.pk]))
        self.assertContains(response, 'aria-modal="true"')

    def test_studio_and_management_pages_share_theme_and_favicon(self):
        self.client.force_login(self.staff)
        for name in ['dashboard_home', 'premium_activate', 'story_list', 'dashboard_shorts', 'story_create', 'short_create']:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assert_brand_head(response)
                self.assertContains(response, '/static/css/dashboard.css')
                self.assertContains(response, 'data-theme-toggle')

    def test_auth_fields_keep_validation_and_accessible_labels(self):
        response = self.client.get(reverse('register'))
        self.assertContains(response, 'for="auth-name"')
        self.assertContains(response, 'id="auth-name"')
        self.assertContains(response, 'for="auth-phone"')
        self.assertContains(response, 'id="auth-phone"')
        response = self.client.post(reverse('login'), {'phone': 'invalid'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['error'])

    def test_error_pages_keep_http_status_and_shared_branding(self):
        from django.test import RequestFactory
        from django.views import defaults
        request = RequestFactory().get('/missing/')
        for status, view in [(400, defaults.bad_request), (403, defaults.permission_denied), (404, defaults.page_not_found), (500, defaults.server_error)]:
            with self.subTest(status=status):
                response = view(request) if status == 500 else view(request, Exception('Private diagnostic details'))
                self.assertEqual(response.status_code, status)
                self.assertContains(response, '/static/css/brand.css', status_code=status)
                self.assertNotContains(response, 'Private diagnostic details', status_code=status)
