from django.db import models


class Channel(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    logo = models.URLField(blank=True, max_length=1000)
    country = models.CharField(max_length=100, blank=True)
    access = models.CharField(max_length=50, blank=True)
    group_title = models.CharField(max_length=255, blank=True, default="Viu")
    urls = models.JSONField(default=dict)

    class Meta:
        ordering = ["name", "id"]

    def __str__(self):
        return self.name
