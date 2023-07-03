from django.db import models
from django.utils import timezone


class Documents(models.Model):
    """
    CLass to save documents object.
    """
    file_key = models.CharField(null=False, blank=False, max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=timezone.now)
    updated_at = models.DateTimeField(auto_now=timezone.now)

