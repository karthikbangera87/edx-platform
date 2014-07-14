from django.db import models

class BadgeClass(models.Model):
    image = models.URLField()
    name = models.CharField(max_length=255)
