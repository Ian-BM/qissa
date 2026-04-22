from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Chapter, Story, StoryAccess


class PaidViewCountingTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            phone="+255712345678",
            name="Reader One",
        )
        self.story = Story.objects.create(
            title="Paid Story",
            description="Story used for paid view tests.",
            price=3000,
            is_published=True,
        )
        self.chapter_five = Chapter.objects.create(
            story=self.story,
            title="Chapter Five",
            content="Paid content",
            order=5,
        )

    def test_story_detail_does_not_increment_views(self):
        self.assertEqual(self.story.views, 0)

        response = self.client.get(reverse("story_detail", args=[self.story.slug]))
        self.assertEqual(response.status_code, 200)

        self.story.refresh_from_db()
        self.assertEqual(self.story.views, 0)

    def test_mark_view_if_needed_counts_only_once(self):
        StoryAccess.objects.create(user=self.user, story=self.story)

        first_mark = StoryAccess.mark_view_if_needed(user=self.user, story=self.story)
        second_mark = StoryAccess.mark_view_if_needed(user=self.user, story=self.story)

        self.assertTrue(first_mark)
        self.assertFalse(second_mark)

        self.story.refresh_from_db()
        self.assertEqual(self.story.views, 1)

    def test_opening_paid_chapter_counts_view_once_for_existing_access(self):
        StoryAccess.objects.create(user=self.user, story=self.story)
        self.client.force_login(self.user)

        first_open = self.client.get(reverse("chapter_reader", args=[self.chapter_five.id]))
        second_open = self.client.get(reverse("chapter_reader", args=[self.chapter_five.id]))

        self.assertEqual(first_open.status_code, 200)
        self.assertEqual(second_open.status_code, 200)

        self.story.refresh_from_db()
        self.assertEqual(self.story.views, 1)
