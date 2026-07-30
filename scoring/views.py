from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count
from .models import Customer
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