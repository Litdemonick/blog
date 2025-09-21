from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from ckeditor_uploader.fields import RichTextUploadingField  # <- con uploader
from taggit.managers import TaggableManager


# ----------------------------
# Perfil de usuario
# ----------------------------
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)

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
    content = RichTextUploadingField()  # editor con subida de archivos/imágenes
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
        """
        Genera slug si no existe. Si el slug ya está tomado, añade un sufijo -2, -3, ...
        para garantizar unicidad sin romper unique=True.
        """
        if not self.slug:
            base = slugify(self.title)[:200] or 'post'
            candidate = base
            i = 2
            while Post.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                # recorta para dejar espacio al sufijo
                candidate = f"{base[:200 - len(str(i)) - 1]}-{i}"
                i += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    @property
    def average_rating(self):
        agg = self.reviews.aggregate(avg=models.Avg('rating'))
        return round(agg['avg'] or 0, 2)


# ----------------------------
# Comentarios (moderados por autor del post)
# ----------------------------
# Comentarios con moderación
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    # TEMPORAL: permitir NULL para backfill
    author = models.ForeignKey(User, on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='comments')
    text = models.TextField()
    is_approved = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']



# ----------------------------
# Reviews 1..5 únicas por (user, post)
# ----------------------------
class Review(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
        constraints = [
            models.UniqueConstraint(fields=['post', 'user'], name='uniq_review_per_user_post')
        ]

    def __str__(self):
        return f'{self.rating}★ de {self.user} en {self.post}'
