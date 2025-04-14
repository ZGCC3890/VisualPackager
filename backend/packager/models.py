from django.db import models
from django.contrib.auth.models import User

class FreightPlan(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    destination = models.CharField(max_length=32, blank=True)
    raw_json    = models.JSONField(null=True, blank=True)   # 方案可空
    title       = models.CharField(max_length=64)           # 列表用
    created     = models.DateTimeField(auto_now_add=True)

class Freight(models.Model):
    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='freights')
    plan         = models.ForeignKey(FreightPlan, on_delete=models.CASCADE,
                                     related_name='items', null=True, blank=True)
    product_name = models.CharField(max_length=100, blank=True, default='')
    length       = models.FloatField()
    width        = models.FloatField()
    height       = models.FloatField()
    weight       = models.FloatField()
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s freight (id={self.id})"