from django.contrib import admin
from .models import Channel


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "country", "group_title", "access")
    list_filter = ("country", "group_title", "access")
    search_fields = ("id", "name", "country")
