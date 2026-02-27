from django.contrib import admin
from .models import Classification


@admin.register(Classification)
class ClassificationAdmin(admin.ModelAdmin):
    list_display = ("create_at", "image_name", "image_path", "prediction_class", "confidence")
    list_filter = ("prediction_class", "create_at")