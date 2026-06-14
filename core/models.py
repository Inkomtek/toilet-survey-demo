from django.db import models


class Rating(models.TextChoices):
    EXCELLENT = 'EXCELLENT', 'Excellent'
    GOOD = 'GOOD', 'Good'
    AVERAGE = 'AVERAGE', 'Average'
    POOR = 'POOR', 'Poor'


class Reason(models.Model):
    rating = models.CharField(max_length=20, choices=Rating.choices)
    text = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['rating', 'order']

    def __str__(self):
        return f"[{self.get_rating_display()}] {self.text}"


class Device(models.Model):
    device_id = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    name = models.CharField(max_length=100, blank=True)
    hotline = models.CharField(max_length=50, blank=True, default='6292 0801')
    is_active = models.BooleanField(default=True)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name or self.device_id


class SurveyResponse(models.Model):
    rating = models.CharField(max_length=20, choices=Rating.choices)
    reason = models.ForeignKey(Reason, on_delete=models.SET_NULL, null=True, blank=True)
    device = models.ForeignKey(Device, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
