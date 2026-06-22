import math
import re

from django.conf import settings
from django.db import models
from django.utils.text import slugify

WORDS_PER_MINUTE = 200


class ShortStory(models.Model):
    CATEGORY_RELATIONSHIP = "relationship"
    CATEGORY_HEARTBREAK = "heartbreak"
    CATEGORY_FAMILY = "family"
    CATEGORY_CAMPUS = "campus"
    CATEGORY_INSPIRATION = "inspiration"
    CATEGORY_MYSTERY = "mystery"
    CATEGORY_LIFE_LESSONS = "life_lessons"

    CATEGORY_CHOICES = [
        (CATEGORY_RELATIONSHIP, "Mahusiano"),
        (CATEGORY_HEARTBREAK, "Huzuni"),
        (CATEGORY_FAMILY, "Familia"),
        (CATEGORY_CAMPUS, "Campus"),
        (CATEGORY_INSPIRATION, "Inspiration"),
        (CATEGORY_MYSTERY, "Mystery"),
        (CATEGORY_LIFE_LESSONS, "Life Lessons"),
    ]

    CATEGORY_EMOJI = {
        CATEGORY_RELATIONSHIP: "❤️",
        CATEGORY_HEARTBREAK: "💔",
        CATEGORY_FAMILY: "👨‍👩‍👧",
        CATEGORY_CAMPUS: "🎓",
        CATEGORY_INSPIRATION: "🌟",
        CATEGORY_MYSTERY: "🔍",
        CATEGORY_LIFE_LESSONS: "📖",
    }

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=280, blank=True)
    cover_image = models.ImageField(upload_to="short_covers/", blank=True, null=True)
    content = models.TextField()
    excerpt = models.TextField(blank=True)
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES)
    read_time = models.PositiveSmallIntegerField(default=1, help_text="Minutes")
    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    featured = models.BooleanField(default=False)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Future compatibility (unused in V1)
    is_premium = models.BooleanField(default=False, editable=False)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="submitted_short_stories",
        editable=False,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "short stories"

    def __str__(self):
        return self.title

    @property
    def category_emoji(self):
        return self.CATEGORY_EMOJI.get(self.category, "📖")

    @property
    def category_label(self):
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)

    @staticmethod
    def calculate_read_time(content):
        words = len(re.findall(r"\w+", content or ""))
        return max(1, math.ceil(words / WORDS_PER_MINUTE))

    def save(self, *args, **kwargs):
        self.read_time = self.calculate_read_time(self.content)
        if not self.excerpt.strip():
            plain = re.sub(r"\s+", " ", self.content or "").strip()
            self.excerpt = plain[:220] + ("..." if len(plain) > 220 else "")
        if not self.slug:
            base_slug = slugify(self.title) or "short-story"
            slug = base_slug
            counter = 1
            while ShortStory.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class ShortStoryLike(models.Model):
    short_story = models.ForeignKey(
        ShortStory, on_delete=models.CASCADE, related_name="story_likes"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="short_story_likes",
    )
    session_key = models.CharField(max_length=40, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["short_story", "user"],
                condition=models.Q(user__isnull=False),
                name="unique_short_like_per_user",
            ),
            models.UniqueConstraint(
                fields=["short_story", "session_key"],
                condition=models.Q(session_key__gt=""),
                name="unique_short_like_per_session",
            ),
        ]


class ShortStoryView(models.Model):
    short_story = models.ForeignKey(
        ShortStory, on_delete=models.CASCADE, related_name="story_views"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="short_story_views",
    )
    session_key = models.CharField(max_length=40, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["short_story", "user"],
                condition=models.Q(user__isnull=False),
                name="unique_short_view_per_user",
            ),
            models.UniqueConstraint(
                fields=["short_story", "session_key"],
                condition=models.Q(session_key__gt=""),
                name="unique_short_view_per_session",
            ),
        ]
