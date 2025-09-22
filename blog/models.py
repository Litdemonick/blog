from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager


# ----------------------------
# Perfil de usuario
# ----------------------------
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, verbose_name="Biografía")

    # 🔹 Nuevos campos añadidos
    name = models.CharField(
        max_length=100, blank=True, null=True,
        verbose_name="Nombre completo",
        help_text="Tu nombre real o el que quieras mostrar públicamente."
    )
    phone = models.CharField(
        max_length=20, blank=True, null=True,
        verbose_name="Teléfono",
        help_text="Número de contacto (opcional)."
    )
    location = models.CharField(
        max_length=100, blank=True, null=True,
        verbose_name="Ubicación",
        help_text="Ciudad o país donde te encuentras."
    )
    interests = models.CharField(
        max_length=255, blank=True, null=True,
        verbose_name="Intereses",
        help_text="Ej: Programación, Música, Deportes..."
    )

    def __str__(self):
        return f'Perfil de {self.user.username}'


# ----------------------------
# Post (noticia o rumor)
# ----------------------------
class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Borrador'),
        ('published', 'Publicado'),
    )

    title = models.CharField(max_length=200, verbose_name='Título')
    slug = models.SlugField(max_length=220, unique=True, db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    cover = models.ImageField(upload_to='covers/', blank=True, null=True)
    excerpt = models.CharField(max_length=300, blank=True)
    content = RichTextUploadingField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True)

    tags = TaggableManager(blank=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.slug])

    def save(self, *args, **kwargs):
        """Genera slug único automáticamente."""
        if not self.slug:
            base = slugify(self.title)[:200] or 'post'
            candidate = base
            i = 2
            while Post.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base[:200 - len(str(i)) - 1]}-{i}"
                i += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    @property
    def average_rating(self):
        agg = self.reviews.aggregate(avg=models.Avg('rating'))
        return round(agg['avg'] or 0, 2)

    @property
    def total_reviews(self):
        return self.reviews.count()


# ----------------------------
# Comentarios (moderados por autor del post)
# ----------------------------
class Comment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pendiente"),
        ("visible", "Visible"),
        ("hidden", "Oculto"),
        ("blocked", "Bloqueado"),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="comments"
    )
    text = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"Comentario de {self.author} en {self.post}"


# ----------------------------
# Reseñas (con rating y moderación)
# ----------------------------
class Review(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pendiente"),
        ("visible", "Visible"),
        ("hidden", "Oculto"),
        ("blocked", "Bloqueado"),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
        constraints = [
            models.UniqueConstraint(fields=['post', 'user'], name='uniq_review_per_user_post')
        ]

    def __str__(self):
        return f"{self.user} – {self.rating}★ – {self.get_status_display()}"

    @property
    def likes_count(self):
        return self.votes.filter(vote="like").count()

    @property
    def dislikes_count(self):
        return self.votes.filter(vote="dislike").count()

    
class PostBlock(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="blocks")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocked_in_posts")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "user")

    def __str__(self):
        return f"{self.user} bloqueado en {self.post}"



# ----------------------------
# Votos en reseñas (like / dislike)
# ----------------------------
class ReviewVote(models.Model):
    VOTE_CHOICES = (
        ('like', '👍'),
        ('dislike', '👎'),
    )

    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_votes')
    vote = models.CharField(max_length=7, choices=VOTE_CHOICES)

    class Meta:
        unique_together = ('review', 'user')

    def __str__(self):
        return f"{self.user.username} → {self.vote} en {self.review}"
