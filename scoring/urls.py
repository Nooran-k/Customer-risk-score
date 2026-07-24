from django.urls import path
from . import views

urlpatterns = [
    path('lookup/', views.customer_lookup, name='customer_lookup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/tier-counts/', views.tier_counts_api, name='tier_counts_api'),
]