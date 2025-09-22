from django.contrib import admin
from .models import Post, Comment, Review, Profile

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'created')
    list_filter = ('status', 'created', 'tags')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ('author',)
    date_hierarchy = 'created'
    ordering = ('-created',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'author', 'status', 'created')
    list_filter = ('status', 'created')
    search_fields = ('text', 'author__username')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'rating', 'created')
    list_filter = ('rating', 'created')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
