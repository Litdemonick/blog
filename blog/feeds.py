from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.contrib.auth.models import User
from taggit.models import Tag

from .models import Post

class AuthorFeed(Feed):
    """ /feeds/author/<username>/ """
    def get_object(self, request, username):
        return get_object_or_404(User, username=username)

    def title(self, obj):
        return f"Posts de {obj.username}"

    def link(self, obj):
        return reverse("blog:post_list")  # ajusta si tienes lista por autor

    def description(self, obj):
        return f"Nuevas entradas publicadas por {obj.username}"

    def items(self, obj):
        return Post.objects.filter(author=obj, status="published").order_by("-created")[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return getattr(item, "excerpt", "") or (item.content[:200] + "…")

    def item_link(self, item):
        return item.get_absolute_url()

class TagFeed(Feed):
    """ /feeds/tag/<slug>/ """
    def get_object(self, request, slug):
        return get_object_or_404(Tag, slug=slug)

    def title(self, obj):
        return f"Posts con tag: {obj.name}"

    def link(self, obj):
        return reverse("blog:post_list")  # ajusta si tienes lista por tag

    def description(self, obj):
        return f"Nuevas entradas etiquetadas como {obj.name}"

    def items(self, obj):
        return Post.objects.filter(tags__in=[obj], status="published").distinct().order_by("-created")[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return getattr(item, "excerpt", "") or (item.content[:200] + "…")

    def item_link(self, item):
        return item.get_absolute_url()
