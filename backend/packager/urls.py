from django.urls import path
from .views import login_view, save_freight_view, plan_view, list_plans_view, plan_detail_view, rename_plan_view, delete_plan_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('freight/', save_freight_view, name='save_freight'),
    path('plan/', plan_view),
    path('plans/', list_plans_view),
    path('plans/<int:pk>/', plan_detail_view),
    path('plans/<int:pk>/rename/', rename_plan_view),
    path('plans/<int:pk>/delete/', delete_plan_view),
]
