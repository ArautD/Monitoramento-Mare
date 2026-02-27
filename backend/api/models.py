from django.db import models

# Create your models here.

class Classification(models.Model):
    create_at = models.DateTimeField(auto_now_add=True)
    image_name = models.CharField(max_length=225, blank=True)
    image_path = models.CharField(max_length=500, blank=True)
    prediction_class = models.CharField(max_length=100)
    confidence = models.FloatField()
    extra_info = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.prediction_class}({self.confidence:2f}) @ {self.create_at}"
        
