from django.db import models
from django.contrib.auth.models import User

class Freight(models.Model):
    """
    货物信息，与 Django 的内置 User 表外键关联
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='freights')
    product_name = models.CharField(max_length=100, blank=True, default='')
    length = models.FloatField()  # 长 (cm)
    width = models.FloatField()   # 宽 (cm)
    height = models.FloatField()  # 高 (cm)
    weight = models.FloatField()  # 重量 (kg)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s freight (id={self.id})"
