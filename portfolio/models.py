from django.db import models
from django.utils.text import slugify

CATEGORY_CHOICES = [
    ('ecommerce', 'E-Commerce'),
    ('restaurant', 'Restaurant'),
    ('portfolio', 'Portfolio'),
    ('real_estate', 'Real Estate'),
    ('health', 'Health & Clinic'),
    ('school', 'School / Education'),
    ('hotel', 'Hotel & Hospitality'),
    ('ngo', 'NGO / Nonprofit'),
    ('other', 'Other'),
]

class WebsiteTemplate(models.Model):
    title        = models.CharField(max_length=100)
    slug         = models.SlugField(unique=True, blank=True)
    category     = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description  = models.TextField()
    thumbnail    = models.ImageField(upload_to='thumbnails/')
    template_name = models.CharField(
        max_length=100,
        help_text="e.g. previews/restaurant.html",
        blank=True
    )
    price        = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_featured  = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-is_featured', '-created_at']
