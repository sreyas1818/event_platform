from django.db import models
from django.contrib.auth.models import User


class Event(models.Model):

    title = models.CharField(max_length=255)

    description = models.TextField()

    language = models.CharField(max_length=100)

    location = models.CharField(max_length=255)

    starts_at = models.DateTimeField()

    ends_at = models.DateTimeField()

    capacity = models.IntegerField(
        null=True,
        blank=True
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Enrollment(models.Model):

    STATUS_CHOICES = (
        ('ENROLLED', 'Enrolled'),
        ('CANCELLED', 'Cancelled')
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE
    )

    seeker = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ENROLLED'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            'event',
            'seeker'
        )