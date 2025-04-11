from django.urls import path
from .views import login_view, save_freight_view, plan_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('freight/', save_freight_view, name='save_freight'),
    path('plan/', plan_view),
]
