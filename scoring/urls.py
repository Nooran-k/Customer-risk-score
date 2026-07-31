from django.urls import path
from . import views

urlpatterns = [
    path('lookup/', views.customer_lookup, name='customer_lookup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/tier-counts/', views.tier_counts_api, name='tier_counts_api'),
    path('api/tier-averages/', views.tier_averages_api, name='tier_averages_api'),
    path('api/loan-grade-by-tier/', views.loan_grade_by_tier_api, name='loan_grade_by_tier_api'),
    path('api/home-ownership/', views.home_ownership_api, name='home_ownership_api'),
    path('api/high-risk-loan-intent/', views.high_risk_loan_intent_api, name='high_risk_loan_intent_api'),
    path('api/risk-by-age-group/', views.risk_by_age_group_api, name='risk_by_age_group_api'),
    path('predict-excel/', views.predict_from_excel, name='predict_from_excel'),
]