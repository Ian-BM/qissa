from django.test import TestCase
from django.urls import reverse
from shorts.models import ShortStory
from stories.models import Story, StoryCategory


class HomepageTests(TestCase):
    def setUp(self):
        self.category = StoryCategory.objects.create(name="Mapenzi", slug="mapenzi")
        self.story = Story.objects.create(title="Long story", description="Test", is_published=True,
                                          category=self.category, views=10)
        self.short = ShortStory.objects.create(title="Short story", content="Test", published=True)
        Story.objects.create(title="Hidden draft", description="Test", is_published=False)

    def test_shorts_appear_before_long_stories_with_shared_compact_cards(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        body = response.content.decode().split("<main", 1)[1].split("</main>", 1)[0]
        self.assertLess(body.index("Simulizi Fupi"), body.index("Simulizi Ndefu"))
        self.assertContains(response, 'class="home-story-grid"', count=2)
        self.assertContains(response, reverse("short_detail", args=[self.short.slug]))
        self.assertContains(response, reverse("story_detail", args=[self.story.slug]))
        self.assertContains(response, reverse("short_list"))
        self.assertContains(response, reverse("stories_list"))
        self.assertNotContains(response, "Hidden draft")

    def test_filters_and_pagination_preserve_visibility_and_short_section(self):
        for filter_name in ["mpya", "maarufu", "mapenzi"]:
            response = self.client.get(reverse("home"), {"filter": filter_name})
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Long story")
            self.assertContains(response, "Short story")
        for index in range(31):
            Story.objects.create(title=f"Extra {index}", description="Test", is_published=True)
        response = self.client.get(reverse("home"), {"filter": "maarufu"})
        self.assertContains(response, "?page=2&filter=maarufu")
        response = self.client.get(reverse("home"), {"filter": "maarufu", "page": 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["stories"].number, 2)

    def test_three_pricing_cards_and_no_obsolete_price(self):
        response = self.client.get(reverse("premium"))
        for price in ["1,000", "3,000", "7,000"]:
            self.assertContains(response, price)
        self.assertContains(response, "Chagua Mpango", count=4)  # title plus three CTAs
        self.assertContains(response, "Thamani Bora")
        self.assertNotContains(response, "5,000")
