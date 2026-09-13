from django import template

register = template.Library()

KNOWN_GENRE_SLUGS = {"mapenzi", "drama", "kusisimua", "mzimu", "kampasi", "maisha"}


@register.filter
def genre_badge(slug):
    if slug in KNOWN_GENRE_SLUGS:
        return f"badge-{slug}"
    return "badge-default"
