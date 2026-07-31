from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count
from .models import Customer
from django.db.models import Avg, Count, Case, When, Value, CharField
import pandas as pd
from django.views.decorators.csrf import csrf_exempt
from .ml_utils import predict_customer

def customer_lookup(request):
    customer = None
    error = None

    if request.method == 'POST':
        customer_id = request.POST.get('customer_id', '').strip()
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            error = f"No customer found with ID '{customer_id}'."

    return render(request, 'scoring/lookup.html', {
        'customer': customer,
        'error': error,
    })

def dashboard(request):
    return render(request, 'scoring/dashboard.html')

def tier_counts_api(request):
    counts = Customer.objects.values('risk_tier').annotate(count=Count('customer_id'))
    data = {row['risk_tier'] or 'Unscored': row['count'] for row in counts}
    return JsonResponse(data)

def tier_averages_api(request):
    data = (
        Customer.objects
        .exclude(risk_tier__isnull=True)
        .values('risk_tier')
        .annotate(
            avg_loan_pct_income=Avg('loan_percent_income'),
            avg_int_rate=Avg('loan_int_rate'),
        )
    )
    result = {
        row['risk_tier']: {
            'avg_loan_pct_income': round(row['avg_loan_pct_income'] or 0, 3),
            'avg_int_rate': round(row['avg_int_rate'] or 0, 2),
        }
        for row in data
    }
    return JsonResponse(result)


def loan_grade_by_tier_api(request):
    data = (
        Customer.objects
        .exclude(risk_tier__isnull=True)
        .values('risk_tier', 'loan_grade')
        .annotate(count=Count('customer_id'))
    )
    result = {}
    for row in data:
        tier = row['risk_tier']
        result.setdefault(tier, {})
        result[tier][row['loan_grade']] = row['count']
    return JsonResponse(result)


def home_ownership_api(request):
    data = (
        Customer.objects
        .values('person_home_ownership')
        .annotate(count=Count('customer_id'))
    )
    result = {row['person_home_ownership']: row['count'] for row in data}
    return JsonResponse(result)


def high_risk_loan_intent_api(request):
    data = (
        Customer.objects
        .filter(risk_tier='High')
        .values('loan_intent')
        .annotate(count=Count('customer_id'))
    )
    result = {row['loan_intent']: row['count'] for row in data}
    return JsonResponse(result)


def risk_by_age_group_api(request):
    data = (
        Customer.objects
        .exclude(risk_score__isnull=True)
        .annotate(
            age_group=Case(
                When(person_age__lt=25, then=Value('20-24')),
                When(person_age__lt=30, then=Value('25-29')),
                When(person_age__lt=35, then=Value('30-34')),
                When(person_age__lt=40, then=Value('35-39')),
                When(person_age__lt=45, then=Value('40-44')),
                When(person_age__lt=50, then=Value('45-49')),
                When(person_age__lt=60, then=Value('50-59')),
                default=Value('60+'),
                output_field=CharField(),
            )
        )
        .values('age_group')
        .annotate(avg_risk=Avg('risk_score'))
        .order_by('age_group')
    )
    result = {row['age_group']: round(row['avg_risk'] or 0, 3) for row in data}
    return JsonResponse(result)

@csrf_exempt
def predict_from_excel(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=400)

    excel_file = request.FILES.get('excel_file')
    if not excel_file:
        return JsonResponse({'error': 'No file uploaded'}, status=400)

    df_upload = pd.read_excel(excel_file)

    results = []
    for _, row in df_upload.iterrows():
        raw_data = row.to_dict()
        prediction = predict_customer(raw_data)

        results.append({
            'person_age': raw_data.get('person_age'),
            'person_income': raw_data.get('person_income'),
            'risk_score': prediction['risk_score'],
            'risk_tier': prediction['risk_tier']
        })

    return JsonResponse({'results': results})